

# from django.urls import path
# from . import views

# app_name = 'posts'

# urlpatterns = [
#     path('', views.PostListCreateView.as_view(), name='post-list'),
    
#     path('<str:pk>/', views.PostDetailView.as_view(), name='post-detail'), 
    
#     path('<str:post_id>/like/', views.LikeToggleView.as_view(), name='like-toggle'),
    
#     path('<str:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
#     path('comments/<str:comment_id>/', views.CommentDeleteView.as_view(), name='comment-delete'),
#     path('comments/<str:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),

    
#     path('<str:post_id>/save/', views.SavePostView.as_view(), name='save-post'),
#     path('saved/', views.SavedPostsListView.as_view(), name='saved-posts'),
#     path('<str:post_id>/saved-status/', views.CheckSavedStatusView.as_view(), name='saved-status'),
#     path('comments/<uuid:comment_id>/', views.CommentUpdateView.as_view(), name='comment-update'),

# ]
from django.urls import path
from . import views
from .views import (
    PostListCreateView,
    PostDetailView,
    LikeToggleView,
    CommentListCreateView,
    CommentDetailView,
    SavePostView,
    SavedPostsListView,
    CheckSavedStatusView,
    VideoPostsListView,      
    TrendingVideosView,     
    SingleVideoView,         
)

app_name = 'posts'

urlpatterns = [
    path('', views.PostListCreateView.as_view(), name='post-list'),
    path('<str:pk>/', views.PostDetailView.as_view(), name='post-detail'),

    path('<str:post_id>/like/', views.LikeToggleView.as_view(), name='like-toggle'),
    
    path('<str:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    
    path('comments/<str:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    path('<str:post_id>/save/', views.SavePostView.as_view(), name='save-post'),
    path('saved/', views.SavedPostsListView.as_view(), name='saved-posts'),
    path('<str:post_id>/saved-status/', views.CheckSavedStatusView.as_view(), name='saved-status'),
    path('videos/', VideoPostsListView.as_view(), name='video-posts'),
    path('videos/trending/', TrendingVideosView.as_view(), name='trending-videos'),
    path('videos/<uuid:post_id>/', SingleVideoView.as_view(), name='single-video'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('debug/user/<uuid:user_id>/posts/', views.DebugUserPostsView.as_view(), name='debug-user-posts'),


]

