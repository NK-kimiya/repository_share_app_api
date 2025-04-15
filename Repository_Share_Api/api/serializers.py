from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User,Room,Category,Repository,GitProject,Message,FavoriteRepository

class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = get_user_model()
        fields = ('email', 'password','username','id')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        #create_user を使って、新しいユーザーを作成
        user = get_user_model().objects.create_user(**validated_data)

        return user

class RoomSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'password', 'owner','owner_name']

        extra_kwargs = {
            'password': {'write_only': True},
            'owner': {'read_only': True}  # これを追加
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        room = Room(**validated_data)
        if password:
            room.set_password(password)
        room.save()
        return room

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class RoomFilterSerializer(serializers.Serializer):
    """パスワードでルームを検索するためのシリアライザー"""
    name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'room']  # 必要なフィールドのみ

class CategoryFilterSerializer(serializers.Serializer):
    """ルームIDを受け取り、カテゴリをフィルタリングするシリアライザー"""
    room_id = serializers.UUIDField()


class RepositorySerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Repository
        fields = ['id', 'url', 'title', 'description', 'demo_video', 'room', 'owner', 'categories']
        extra_kwargs = {
            'owner': {'read_only': True}  # `owner` は自動で設定するのでリクエスト不要
        }

    def create(self, validated_data):
        """リポジトリ作成時にカテゴリをセット"""
        categories = validated_data.pop('categories', [])  # `categories` を取得
        repository = Repository.objects.create(**validated_data)  # リポジトリ作成
        repository.categories.set(categories)  # ManyToMany の関連付け
        return repository

class RepositoryFilterSerializer(serializers.Serializer):
    """Room ID でリポジトリをフィルタリングするシリアライザー"""
    room_id = serializers.UUIDField()

class GitProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitProject
        fields = ['id', 'title', 'text', 'subheading1', 'url1', 'subheading2', 'url2', 'subheading3', 'url3']

class MessageSelializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id','content','repository','created_at','user_name']
        read_only_fields = ['id','created_at','user_name']

#お気に入りのモデル用のシリアライザー
class FavoriteRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRepository
        fields = ['id', 'repository']
        read_only_fields = ['id']  # userはビューでセットする


