from rest_framework import routers
from django.urls import path
from django.conf.urls import include
from .views import CreateUserView,MessageCreateAPIView,RepositoryMessageListAPIView
from .views import CreateRoomView,RoomPasswordFilterView,CreateCategoryView,CategoryFilterView,CreateRepositoryView,RepositoryFilterView,predict_category,GitProjectSearchView,CurrentUserAPIView
router = routers.DefaultRouter()


urlpatterns = [
    path('',include(router.urls)),
    path('create/', CreateUserView.as_view(), name='create'),
    path('rooms/', CreateRoomView.as_view(), name='create-room'),
    path('rooms/filter/', RoomPasswordFilterView.as_view(), name='room-filter'),
    path('categories/', CreateCategoryView.as_view(), name='create-category'),
    path('categories/filter/', CategoryFilterView.as_view(), name='category-filter'),
    path('repositories/', CreateRepositoryView.as_view(), name='create-repository'),
    path('repositories/filter/', RepositoryFilterView.as_view(), name='repository-filter'),
    path('predict/', predict_category, name='predict_category'),
    path('gitprojects/search/', GitProjectSearchView.as_view(), name='gitproject-search'),
    path('messages/create/', MessageCreateAPIView.as_view(), name='message-create'),
    path('messages/repository/<uuid:repository_id>/', RepositoryMessageListAPIView.as_view(), name='repository-messages'),
    path('user/current/', CurrentUserAPIView.as_view(), name='current-user'),
]