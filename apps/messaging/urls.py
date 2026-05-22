
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import views

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'conversations/(?P<conversation_pk>[0-9a-f-]+)/messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    
    path('start-conversation/', views.StartConversationView.as_view(), name='start-conversation'),
    
    path('analyze-target/<str:user_id>/', views.TargetAnalysisView.as_view(), name='analyze-target'),
    path('suggestions/opening/<str:user_id>/', views.OpeningMessageSuggestionsView.as_view(), name='opening-suggestions'),
    path('suggestions/reply/', views.ReplySuggestionView.as_view(), name='reply-suggestion'),
    path('icebreakers/<str:user_id>/', views.IceBreakerTopicsView.as_view(), name='icebreakers'),
    path('start-with-ai/', views.StartConversationWithAIAssistView.as_view(), name='start-with-ai'),
]

from .views import (
    GroupConversationViewSet, GroupMessageViewSet,
    GroupDetailView, AddMemberToGroupView, RemoveMemberFromGroupView, LeaveGroupView
)

group_router = DefaultRouter()
group_router.register(r'groups', GroupConversationViewSet, basename='group')
group_router.register(r'groups/(?P<group_pk>[0-9a-f-]+)/messages', GroupMessageViewSet, basename='group-messages')

urlpatterns += [
    path('groups/<str:group_id>/detail/', GroupDetailView.as_view(), name='group-detail'),
    path('groups/<str:group_id>/add-member/', AddMemberToGroupView.as_view(), name='add-member'),
    path('groups/<str:group_id>/remove-member/<str:user_id>/', RemoveMemberFromGroupView.as_view(), name='remove-member'),
    path('groups/<str:group_id>/leave/', LeaveGroupView.as_view(), name='leave-group'),
]

urlpatterns += group_router.urls