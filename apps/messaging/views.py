# apps/messaging/views.py

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.pagination import MessagesPagination

User = get_user_model()


# ========== ViewSetهای قبلی ==========

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagesPagination

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagesPagination

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
        ).select_related('sender')

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = Conversation.objects.get(id=conversation_id)
        serializer.save(
            conversation=conversation,
            sender=self.request.user
        )
        
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message_at'])

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None, conversation_pk=None):
        messages = Message.objects.filter(
            conversation_id=conversation_pk,
            sender__not=request.user,
            is_read=False
        )
        messages.update(is_read=True, read_at=timezone.now())
        return Response({'status': 'marked as read'})


# ========== دستیار هوشمند مخ‌زنی ==========

class TargetAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        
        return Response({
            "success": True,
            "data": {
                "target_username": target.username,
                "analysis": {
                    "personality_type": "دوستانه و صمیمی",
                    "interests": ["هنر", "موسیقی", "سفر"],
                    "communication_style": "صمیمی",
                    "icebreakers": ["سلام! چطوری؟", "چه خبر؟"],
                    "topics_to_avoid": ["سیاست"],
                    "best_time_to_message": "عصرها",
                    "tips": ["با احترام صحبت کن", "بهش فرصت بده"]
                },
                "advice": "با این فرد صمیمی و محترمانه صحبت کن"
            }
        })


class OpeningMessageSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        count = min(int(request.query_params.get('count', 3)), 5)
        
        suggestions = [
            "سلام! حال دیدن پست‌هات خوب بود 😊",
            "چطوری؟ پروفایل جالبی داری! 👋",
            "سلام! چه کار می‌کنی؟ 🌟",
            "سلام! امیدوارم روز خوبی داشته باشی ✨",
            "چطوری؟ دوست داشتم باهات آشنا بشم 🤝"
        ][:count]
        
        return Response({
            "success": True,
            "data": {
                "target": target.username,
                "suggestions": suggestions
            }
        })


class ReplySuggestionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        last_message = request.data.get('last_message', '').strip()
        
        if not last_message:
            return Response({"success": False, "error": "last_message الزامی است"}, status=400)
        
        return Response({
            "success": True,
            "data": {
                "suggested_reply": "چه جالب! بگو بیشتر برام 😊"
            }
        })


class IceBreakerTopicsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        
        return Response({
            "success": True,
            "data": {
                "target": target.username,
                "personality": "دوستانه",
                "topics_to_start": ["علایق مشترک", "فیلم و سریال", "موسیقی", "سفر"],
                "topics_to_avoid": ["سیاست", "مسائل شخصی خیلی خصوصی"]
            }
        })


class StartConversationWithAIAssistView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        target_id = request.data.get('target_id')
        
        if not target_id:
            return Response({"success": False, "error": "target_id الزامی است"}, status=400)
        
        target = get_object_or_404(User, id=target_id)
        
        if request.user == target:
            return Response({"success": False, "error": "نمی‌توانید با خودتان چت کنید"}, status=400)
        
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=target
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, target)
        
        return Response({
            "success": True,
            "data": {
                "conversation_id": conversation.id,
                "target": target.username,
                "suggested_message": "سلام! چطوری؟ از پست‌هات خوشم اومد 😊"
            }
        })