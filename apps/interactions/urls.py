# apps/interactions/urls.py

from django.urls import path
from .views import (
    TrackPostView,
    BulkTrackView,
    FeedView,
    ExploreView,
    ComparePostView,
    PostStatsView
)

urlpatterns = [
    # Tracking
    path('track/<uuid:post_id>/', TrackPostView.as_view(), name='track-post'),
    path('track/bulk/', BulkTrackView.as_view(), name='track-bulk'),
    
    # Feed & Explore
    path('feed/', FeedView.as_view(), name='feed'),
    path('explore/', ExploreView.as_view(), name='explore'),
    
    # Compare & Stats
    path('compare/<uuid:post_id>/', ComparePostView.as_view(), name='compare-post'),
    path('stats/<uuid:post_id>/', PostStatsView.as_view(), name='post-stats'),
]