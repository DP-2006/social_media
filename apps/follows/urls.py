







# apps/follows/urls.py

from django.urls import path
from . import views

app_name = 'follows'

urlpatterns = [
    path('toggle/<str:user_id>/', views.FollowToggleView.as_view(), name='follow-toggle'),
    
    path('follow/<str:user_id>/', views.FollowUserView.as_view(), name='follow-user'),
    
    path('unfollow/<str:user_id>/', views.UnfollowUserView.as_view(), name='unfollow-user'),
    
    path('users/<str:user_id>/followers/', views.FollowersListView.as_view(), name='followers-list'),
    
    path('users/<str:user_id>/following/', views.FollowingListView.as_view(), name='following-list'),
    
  
    path('users/<str:user_id>/counts/', views.FollowCountView.as_view(), name='follow-counts'),
]