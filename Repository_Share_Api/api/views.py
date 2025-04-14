from tokenize import tokenize

from rest_framework import viewsets
from rest_framework import generics, permissions
from transformers import BertForSequenceClassification

from .serializers import UserSerializer,RoomSerializer,RoomFilterSerializer,CategorySerializer,CategoryFilterSerializer,RepositorySerializer,RepositoryFilterSerializer,GitProjectSerializer,MessageSelializer
from rest_framework.permissions import AllowAny
from .models import Room,Category,Repository,GitProject,Message
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import views, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

#自然言語機能
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .classifier import TextClassifier

import requests
import uuid
from rest_framework.decorators import action


# 初期化はアプリ起動時に一度だけ
classifier = TextClassifier()

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_category(request):
    try:
        # リクエストボディからtext取得
        text = request.data.get('text')

        if not text:
            return Response({'error': 'テキストが未入力です。'}, status=status.HTTP_400_BAD_REQUEST)

        # モデルで予測
        predicted_category, predicted_probability = classifier.predict_category(text)

        # 結果をJSONで返す
        return Response({
            'category': predicted_category,
            'probability': predicted_probability
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create your views here.
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class CreateRoomView(generics.CreateAPIView):
    serializer_class = RoomSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RoomPasswordFilterView(views.APIView):
    """パスワードでルームを検索する API"""

    def post(self, request, *args, **kwargs):
        serializer = RoomFilterSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']  # パスワードを取得

            # すべてのルームを取得し、パスワードが一致するものを探す
            matching_rooms = []
            for room in Room.objects.all():
                if check_password(password, room.password):  # パスワードが一致するか確認
                    matching_rooms.append(room)

            # 一致するルームをシリアライズしてレスポンス
            if matching_rooms:
                return Response(RoomSerializer(matching_rooms, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No matching rooms found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateCategoryView(generics.CreateAPIView):
    """カテゴリ作成API"""
    serializer_class = CategorySerializer


class CategoryFilterView(views.APIView):
    """ルームIDでカテゴリをフィルタリングするAPI"""
    def post(self, request, *args, **kwargs):
        serializer = CategoryFilterSerializer(data=request.data)
        if serializer.is_valid():
            room_id = serializer.validated_data['room_id']
            categories = Category.objects.filter(room_id=room_id)
            if not categories.exists():
                return Response({"detail": "No categories found for this room."}, status=status.HTTP_404_NOT_FOUND)

            return Response(CategorySerializer(categories, many=True).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateRepositoryView(generics.CreateAPIView):
    """リポジトリ作成 API"""
    serializer_class = RepositorySerializer

    def perform_create(self, serializer):
        """リポジトリ作成時に `owner` をログインユーザーに設定"""
        serializer.save(owner=self.request.user)


class RepositoryFilterView(views.APIView):
    """Room ID でリポジトリをフィルタリングする API"""
    def post(self, request, *args, **kwargs):
        serializer = RepositoryFilterSerializer(data=request.data)#React などのクライアントから送られた JSON データ（room_id）をバリデーション
        if serializer.is_valid():
            room_id = serializer.validated_data['room_id']
            repositories = Repository.objects.filter(room_id=room_id)#room_id に一致する Repository モデルのオブジェクトを Django ORM で取得
            serialized_data = RepositorySerializer(repositories, many=True).data#RepositorySerializer を使って、DBオブジェクト → JSON形式に変換

            # UUID を文字列にして抽出
            repository_ids = [str(repo['id']) for repo in serialized_data]#Repository の id を UUID → 文字列 にして抽出
            username = request.user.username if request.user.is_authenticated else 'anonymous'#ログイン済みのユーザーなら username を取得
            print("リクエストユーザーは" + username)

            # Node.jsへPOST
            read_count_response = requests.post(#Node.js の /read_count_filter に repository_ids + username を送信
                'http://localhost:4000/read_count_filter',
                json={'repository_ids': repository_ids, 'username': username},
                timeout=5
            )

            #Node.jsから返ってきたデータを辞書に変換
            read_count_map = {}
            if read_count_response.status_code == 200:
                for item in read_count_response.json().get("data", []):
                    read_count_map[item["roomId"]] = item["readCount"]

            #各 repo の id に対応する readCount を追加
            for repo in serialized_data:
                repo_id = str(repo["id"])
                print("書き換える値は"+str(read_count_map.get(repo_id, 0)))
                repo["readCount"] = read_count_map.get(repo_id, 0)

            # レスポンスとして返す
            return Response(serialized_data, status=status.HTTP_200_OK)

class GitProjectSearchView(APIView):
    """
    GitProject を title で検索する専用のView（POSTリクエスト、認証不要）
    """
    permission_classes = (AllowAny,)  # 認証不要

    def post(self, request):
        # POSTなので request.data を使用
        title_query = request.data.get('title', None)

        # titleが未入力の場合
        if not title_query:
            return Response({"error": "title パラメータを指定してください。"}, status=status.HTTP_400_BAD_REQUEST)

        # カテゴリ分類の予測（モデルが既にある前提）
        predicted_category, predicted_probability = classifier.predict_category(title_query)
        print("分類結果：" + predicted_category)

        # GitProject をタイトルで部分一致検索
        projects = GitProject.objects.filter(title__icontains=title_query)

        # 検索結果をシリアライズ
        serializer = GitProjectSerializer(projects, many=True)

        # レスポンスにまとめる
        response_data = {
            "predicted_category": predicted_category,
            "predicted_probability": predicted_probability,
            "projects": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    #MessageモデルのAPI

class MessageCreateAPIView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSelializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RepositoryMessageListAPIView(generics.ListAPIView):
    serializer_class = MessageSelializer

    def get_queryset(self):
        repository_id = self.kwargs['repository_id']
        return Message.objects.filter(repository__id=repository_id)

class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
        })

#リポジトリーのカテゴリー検索
class RepositoryReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    @action(detail=False, methods=["get"])
    def filter_by_categories(self, request):
        category_ids = request.query_params.getlist("category")
        room_id_str = request.query_params.get("room")

        print("----- フィルタ開始 -----")
        print("リクエストされたカテゴリID一覧:", category_ids)
        print("リクエストされたルームID:", room_id_str)

        if not category_ids or not room_id_str:
            print("カテゴリまたはルームが指定されていません。")
            return Response([])

        try:
            room_id = uuid.UUID(room_id_str)
        except ValueError:
            print("room_idの形式が不正です")
            return Response({"error": "room_idの形式がUUIDではありません"}, status=400)

        queryset = Repository.objects.filter(
            categories__id__in=category_ids,
            room__id=room_id
        ).distinct()

        print("フィルタ後のクエリセット件数:", queryset.count())

        # Django → JSON
        serialized_data = self.get_serializer(queryset, many=True).data
        # 1. RepositoryのUUIDをstr化
        repository_ids = [str(repo["id"]) for repo in serialized_data]
        # 2. ユーザー名の取得
        username = request.user.username if request.user.is_authenticated else "anonymous"

        # 3. Node.jsへPOSTしてreadCountを取得
        read_count_map = {}
        try:
            response = requests.post(
                "http://localhost:4000/read_count_filter",
                json={"repository_ids": repository_ids, "username": username},
                timeout=5
            )
            if response.status_code == 200:
                for item in response.json().get("data", []):
                    read_count_map[item["roomId"]] = item["readCount"]
        except requests.RequestException as e:
            print("Node.js連携エラー:", e)

        # 4. readCountをserialized_dataに付加
        for repo in serialized_data:
            repo_id = str(repo["id"])
            repo["readCount"] = read_count_map.get(repo_id, 0)

        print("----- フィルタ終了 -----")

        return Response(serialized_data)