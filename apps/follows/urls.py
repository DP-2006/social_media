# # apps/follows/urls.py

# from django.urls import path
# from . import views

# app_name = 'follows'

# urlpatterns = [
#     path('toggle/<uuid:user_id>/', views.FollowToggleView.as_view(), name='follow-toggle'),
    
#     path('users/<uuid:user_id>/followers/', views.FollowersListView.as_view(), name='followers-list'),
#     path('users/<uuid:user_id>/following/', views.FollowingListView.as_view(), name='following-list'),
    
#     path('users/<uuid:user_id>/counts/', views.FollowCountsView.as_view(), name='follow-counts'),
    
#     path('check/', views.CheckFollowStatusView.as_view(), name='follow-check'),
# ]





# apps/follows/urls.py

from django.urls import path
from . import views

app_name = 'follows'

urlpatterns = [
    path('toggle/<int:user_id>/', views.FollowToggleView.as_view(), name='follow-toggle'),
    
    path('follow/<int:user_id>/', views.FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', views.UnfollowUserView.as_view(), name='unfollow-user'),
    
    path('users/<int:user_id>/followers/', views.FollowersListView.as_view(), name='followers-list'),
    path('users/<int:user_id>/following/', views.FollowingListView.as_view(), name='following-list'),
    
    path('users/<int:user_id>/counts/', views.FollowCountView.as_view(), name='follow-counts'),
]