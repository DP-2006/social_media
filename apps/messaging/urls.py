# apps/messaging/urls.py

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ConversationViewSet, MessageViewSet

# router = DefaultRouter()
# router.register('', ConversationViewSet, basename='conversation')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('<int:conversation_pk>/messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='conversation-messages'),
#     path('<int:conversation_pk>/messages/mark-read/', MessageViewSet.as_view({'post': 'mark_read'}), name='mark-read'),
# ]





# apps/messaging/urls.py

# from django.urls import path
# from . import views

# app_name = 'messaging'

# urlpatterns = [
#     path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
#     path('conversations/start/', views.StartConversationView.as_view(), name='start-conversation'),
#     path('conversations/<int:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
#     path('conversations/<int:conversation_id>/send/', views.SendMessageView.as_view(), name='send-message'),
    
#     path('analyze-target/<int:user_id>/', views.TargetAnalysisView.as_view(), name='analyze-target'),
#     path('suggestions/opening/<int:user_id>/', views.OpeningMessageSuggestionsView.as_view(), name='opening-suggestions'),
#     path('suggestions/reply/', views.ReplySuggestionView.as_view(), name='reply-suggestion'),
#     path('icebreakers/<int:user_id>/', views.IceBreakerTopicsView.as_view(), name='icebreakers'),
# ]











# apps/messaging/urls.py
# apps/messaging/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import views

# ایجاد router
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'conversations/(?P<conversation_pk>[0-9]+)/messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    # مسیرهای ViewSet (دایرکت اصلی)
    path('', include(router.urls)),
    
    # مسیرهای دستیار هوشمند (APIViewها)
    path('analyze-target/<int:user_id>/', views.TargetAnalysisView.as_view(), name='analyze-target'),
    path('suggestions/opening/<int:user_id>/', views.OpeningMessageSuggestionsView.as_view(), name='opening-suggestions'),
    path('suggestions/reply/', views.ReplySuggestionView.as_view(), name='reply-suggestion'),
    path('icebreakers/<int:user_id>/', views.IceBreakerTopicsView.as_view(), name='icebreakers'),
    path('start-with-ai/', views.StartConversationWithAIAssistView.as_view(), name='start-with-ai'),
]