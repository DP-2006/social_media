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
from apps.blocks.views import BlockedUsersMixin

from .models import GroupConversation, GroupMessage, GroupMember
from .serializers import (
    GroupConversationSerializer, GroupMessageSerializer,
    CreateGroupSerializer, AddMemberToGroupSerializer
)

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet, BlockedUsersMixin):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagesPagination

    def get_queryset(self):
        blocked_ids = self.get_mutually_blocked_ids(self.request.user)
        return Conversation.objects.filter(
            participants=self.request.user
        ).exclude(
            participants__id__in=blocked_ids
        ).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet, BlockedUsersMixin):
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
        
        other_user = conversation.participants.exclude(id=self.request.user.id).first()
        if other_user:
            blocked_ids = self.get_mutually_blocked_ids(self.request.user)
            if other_user.id in blocked_ids:
                raise PermissionError("نمی‌توانید به این کاربر پیام دهید (بلاک شده)")
        
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

class StartConversationView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        target_id = request.data.get('target_id')
        
        if not target_id:
            return Response({"success": False, "error": "target_id الزامی است"}, status=400)
        
        target = get_object_or_404(User, id=target_id)
        
        if request.user == target:
            return Response({"success": False, "error": "نمی‌توانید با خودتان چت کنید"}, status=400)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False, 
                "error": "نمی‌توانید با این کاربر پیام دهید (بلاک شده)"
            }, status=status.HTTP_403_FORBIDDEN)
        
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
                "target_id": target.id
            }
        }, status=status.HTTP_200_OK)



class TargetAnalysisView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False,
                "error": "این کاربر را بلاک کرده‌اید"
            }, status=status.HTTP_403_FORBIDDEN)
        
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


class OpeningMessageSuggestionsView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        count = min(int(request.query_params.get('count', 3)), 5)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False,
                "error": "این کاربر را بلاک کرده‌اید"
            }, status=status.HTTP_403_FORBIDDEN)
        
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


class IceBreakerTopicsView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False,
                "error": "این کاربر را بلاک کرده‌اید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            "success": True,
            "data": {
                "target": target.username,
                "personality": "دوستانه",
                "topics_to_start": ["علایق مشترک", "فیلم و سریال", "موسیقی", "سفر"],
                "topics_to_avoid": ["سیاست", "مسائل شخصی خیلی خصوصی"]
            }
        })


class StartConversationWithAIAssistView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        target_id = request.data.get('target_id')
        
        if not target_id:
            return Response({"success": False, "error": "target_id الزامی است"}, status=400)
        
        target = get_object_or_404(User, id=target_id)
        
        if request.user == target:
            return Response({"success": False, "error": "نمی‌توانید با خودتان چت کنید"}, status=400)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False, 
                "error": "نمی‌توانید با این کاربر پیام دهید (بلاک شده)"
            }, status=status.HTTP_403_FORBIDDEN)
        
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



class GroupConversationViewSet(viewsets.ModelViewSet, BlockedUsersMixin):
    serializer_class = GroupConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GroupConversation.objects.filter(
            members=self.request.user,
            is_active=True
        ).prefetch_related('members', 'messages')
    
    def create(self, request):
        serializer = CreateGroupSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        
        return Response({
            "success": True,
            "data": GroupConversationSerializer(group, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class GroupMessageViewSet(viewsets.ModelViewSet, BlockedUsersMixin):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        group_id = self.kwargs.get('group_pk')
        return GroupMessage.objects.filter(
            conversation_id=group_id,
            conversation__members=self.request.user
        ).select_related('sender')
    
    def perform_create(self, serializer):
        group_id = self.kwargs.get('group_pk')
        group = get_object_or_404(GroupConversation, id=group_id)
        
        if not group.members.filter(id=self.request.user.id).exists():
            raise PermissionError("شما عضو این گروه نیستید")
        
        message = serializer.save(
            conversation=group,
            sender=self.request.user
        )
        
        group.last_message_at = timezone.now()
        group.last_message_preview = message.content[:100]
        group.save(update_fields=['last_message_at', 'last_message_preview'])
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None, group_pk=None):
        message = self.get_object()
        
        if message.sender == request.user:
            return Response({"error": "نمی‌توانید پیام خودتان را مارک کنید"}, status=400)
        
        message.mark_as_read(request.user)
        
        return Response({
            "success": True,
            "message": "پیام به عنوان خوانده شده علامت‌گذاری شد"
        })


class GroupDetailView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if not group.members.filter(id=request.user.id).exists():
            return Response({"error": "شما عضو این گروه نیستید"}, status=403)
        
        serializer = GroupConversationSerializer(group, context={'request': request})
        
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def delete(self, request, group_id):
        group = get_object_or_404(GroupConversation, id=group_id)
        
        if group.admin != request.user:
            return Response({"error": "فقط مدیر گروه می‌تواند گروه را حذف کند"}, status=403)
        
        group.is_active = False
        group.save(update_fields=['is_active'])
        
        return Response({"success": True, "message": "گروه با موفقیت حذف شد"})


class AddMemberToGroupView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, group_id):
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if group.admin != request.user:
            return Response({"error": "فقط مدیر گروه می‌تواند عضو اضافه کند"}, status=403)
        
        serializer = AddMemberToGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data['user_ids']
        added_users = []
        
        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)
            
            if not self.can_interact(request.user, user):
                continue
            
            if not group.members.filter(id=user_id).exists():
                group.members.add(user)
                GroupMember.objects.create(group=group, user=user, role='member')
                added_users.append(user.username)
        
        return Response({
            "success": True,
            "message": f"{len(added_users)} کاربر با موفقیت اضافه شدند",
            "added_users": added_users
        }, status=status.HTTP_200_OK)


class RemoveMemberFromGroupView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, group_id, user_id):
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if group.admin != request.user and request.user.id != user_id:
            return Response({"error": "شما اجازه حذف این عضو را ندارید"}, status=403)
        
        target_user = get_object_or_404(User, id=user_id)
        
        if not group.members.filter(id=user_id).exists():
            return Response({"error": "این کاربر عضو گروه نیست"}, status=400)
        
        group.members.remove(target_user)
        GroupMember.objects.filter(group=group, user=target_user).delete()
        
        return Response({
            "success": True,
            "message": f"{target_user.username} از گروه حذف شد"
        }, status=status.HTTP_200_OK)


class LeaveGroupView(APIView, BlockedUsersMixin):
    """خروج از گروه"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, group_id):
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if not group.members.filter(id=request.user.id).exists():
            return Response({"error": "شما عضو این گروه نیستید"}, status=400)
        
        if group.admin == request.user and group.members.count() == 1:
            group.is_active = False
            group.save(update_fields=['is_active'])
            return Response({"success": True, "message": "گروه به دلیل خالی شدن حذف شد"})
        
        if group.admin == request.user:
            new_admin = group.members.exclude(id=request.user.id).first()
            if new_admin:
                group.admin = new_admin
                group.save(update_fields=['admin'])
        
        group.members.remove(request.user)
        GroupMember.objects.filter(group=group, user=request.user).delete()
        
        return Response({
            "success": True,
            "message": "شما از گروه خارج شدید"
        }, status=status.HTTP_200_OK)