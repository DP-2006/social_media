# apps/posts/urls.py

from django.urls import path
from . import views
urlpatterns = [
    path('', views.PostListCreateView.as_view(), name='post-list'),
    path('<str:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    
    path('<str:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'), 
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    path('<str:post_id>/like/', views.LikePostView.as_view(), name='like-post'),  
]