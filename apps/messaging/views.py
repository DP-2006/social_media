# apps/messaging/views.py

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, MessageSerializer,
    GroupConversationSerializer, GroupMessageSerializer,
    CreateGroupSerializer, AddMemberToGroupSerializer,
    StartConversationSerializer, TargetAnalysisSerializer,
    OpeningMessageSuggestionsSerializer, ReplySuggestionSerializer,
    IceBreakerTopicsSerializer, ConversationIdSerializer,
    GroupDetailSerializer, MemberActionSerializer, LeaveGroupSerializer
)
from core.pagination import MessagesPagination
from apps.blocks.views import BlockedUsersMixin

from .models import GroupConversation, GroupMessage, GroupMember

User = get_user_model()


class ConversationViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, BlockedUsersMixin):
    """
    ViewSet for managing private conversations
    """
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


class MessageViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, BlockedUsersMixin):
    """
    ViewSet for managing messages in conversations
    """
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

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None, conversation_pk=None):
        """
        Mark all messages in conversation as read
        """
        messages = Message.objects.filter(
            conversation_id=conversation_pk,
            sender__not=request.user,
            is_read=False
        )
        messages.update(is_read=True, read_at=timezone.now())
        return Response({'status': 'marked as read', 'success': True})


class StartConversationView(GenericAPIView, BlockedUsersMixin):
    """
    Start a new conversation with a user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StartConversationSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_id = serializer.validated_data['target_id']
        target = get_object_or_404(User, id=target_id)
        
        if request.user == target:
            return Response({"success": False, "error": "نمی‌توانید با خودتان چت کنید"}, status=status.HTTP_400_BAD_REQUEST)
        
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


class TargetAnalysisView(GenericAPIView, BlockedUsersMixin):
    """
    Get personality analysis for a target user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TargetAnalysisSerializer
    
    def get(self, request, user_id):
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        
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


class OpeningMessageSuggestionsView(GenericAPIView, BlockedUsersMixin):
    """
    Get AI-powered opening message suggestions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OpeningMessageSuggestionsSerializer
    
    def get(self, request, user_id):
        # Validate query parameters
        query_serializer = self.get_serializer(data={
            'user_id': user_id,
            'count': request.query_params.get('count', 3)
        })
        query_serializer.is_valid(raise_exception=True)
        
        target = get_object_or_404(User, id=user_id)
        count = query_serializer.validated_data['count']
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target.id in blocked_ids:
            return Response({
                "success": False,
                "error": "این کاربر را بلاک کرده‌اید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        suggestions = [
            "سلام! حال دیدن پست‌هات خوب بود ",
            "چطوری؟ پروفایل جالبی داری! ",
            "سلام! چه کار می‌کنی؟ ",
            "سلام! امیدوارم روز خوبی داشته باشی ",
            "چطوری؟ دوست داشتم باهات آشنا بشم "
        ][:count]
        
        return Response({
            "success": True,
            "data": {
                "target": target.username,
                "suggestions": suggestions
            }
        })


class ReplySuggestionView(GenericAPIView):
    """
    Get AI-powered reply suggestions based on last message
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReplySuggestionSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        last_message = serializer.validated_data['last_message']
        
        return Response({
            "success": True,
            "data": {
                "suggested_reply": "چه جالب!"
            }
        })


class IceBreakerTopicsView(GenericAPIView, BlockedUsersMixin):
    """
    Get icebreaker topics for starting conversation
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TargetAnalysisSerializer
    
    def get(self, request, user_id):
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        
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


class StartConversationWithAIAssistView(GenericAPIView, BlockedUsersMixin):
    """
    Start conversation with AI-powered message suggestion
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StartConversationSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_id = serializer.validated_data['target_id']
        target = get_object_or_404(User, id=target_id)
        
        if request.user == target:
            return Response({"success": False, "error": "نمی‌توانید با خودتان چت کنید"}, status=status.HTTP_400_BAD_REQUEST)
        
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
                "suggested_message": "سلام! چطوری؟ از پست‌هات خوشم اومد "
            }
        })


class GroupConversationViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, BlockedUsersMixin):
    """
    ViewSet for managing group conversations
    """
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


class GroupMessageViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, BlockedUsersMixin):
    """
    ViewSet for managing messages in group conversations
    """
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
        """
        Mark a specific message as read
        """
        message = self.get_object()
        
        if message.sender == request.user:
            return Response({"error": "نمی‌توانید پیام خودتان را مارک کنید"}, status=status.HTTP_400_BAD_REQUEST)
        
        message.mark_as_read(request.user)
        
        return Response({
            "success": True,
            "message": "پیام به عنوان خوانده شده علامت‌گذاری شد"
        })


class GroupDetailView(GenericAPIView, BlockedUsersMixin):
    """
    Get or delete group conversation details
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GroupDetailSerializer
    
    def get(self, request, group_id):
        serializer = self.get_serializer(data={'group_id': group_id})
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if not group.members.filter(id=request.user.id).exists():
            return Response({"error": "شما عضو این گروه نیستید"}, status=status.HTTP_403_FORBIDDEN)
        
        response_serializer = GroupConversationSerializer(group, context={'request': request})
        
        return Response({
            "success": True,
            "data": response_serializer.data
        })
    
    def delete(self, request, group_id):
        serializer = self.get_serializer(data={'group_id': group_id})
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(GroupConversation, id=group_id)
        
        if group.admin != request.user:
            return Response({"error": "فقط مدیر گروه می‌تواند گروه را حذف کند"}, status=status.HTTP_403_FORBIDDEN)
        
        group.is_active = False
        group.save(update_fields=['is_active'])
        
        return Response({"success": True, "message": "گروه با موفقیت حذف شد"})


class AddMemberToGroupView(GenericAPIView, BlockedUsersMixin):
    """
    Add members to a group conversation
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddMemberToGroupSerializer
    
    def post(self, request, group_id):
        serializer = self.get_serializer(data={
            'group_id': group_id,
            'user_ids': request.data.get('user_ids', [])
        })
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if group.admin != request.user:
            return Response({"error": "فقط مدیر گروه می‌تواند عضو اضافه کند"}, status=status.HTTP_403_FORBIDDEN)
        
        user_ids = serializer.validated_data['user_ids']
        added_users = []
        
        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)
            
            # Check block status
            blocked_ids = self.get_mutually_blocked_ids(request.user)
            if user.id in blocked_ids:
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


class RemoveMemberFromGroupView(GenericAPIView, BlockedUsersMixin):
    """
    Remove a member from group conversation
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemberActionSerializer
    
    def delete(self, request, group_id, user_id):
        serializer = self.get_serializer(data={
            'group_id': group_id,
            'user_id': user_id
        })
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if group.admin != request.user and request.user.id != user_id:
            return Response({"error": "شما اجازه حذف این عضو را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        
        target_user = get_object_or_404(User, id=user_id)
        
        if not group.members.filter(id=user_id).exists():
            return Response({"error": "این کاربر عضو گروه نیست"}, status=status.HTTP_400_BAD_REQUEST)
        
        group.members.remove(target_user)
        GroupMember.objects.filter(group=group, user=target_user).delete()
        
        return Response({
            "success": True,
            "message": f"{target_user.username} از گروه حذف شد"
        }, status=status.HTTP_200_OK)


class LeaveGroupView(GenericAPIView, BlockedUsersMixin):
    """
    Leave a group conversation
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveGroupSerializer
    
    def post(self, request, group_id):
        serializer = self.get_serializer(data={'group_id': group_id})
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(GroupConversation, id=group_id, is_active=True)
        
        if not group.members.filter(id=request.user.id).exists():
            return Response({"error": "شما عضو این گروه نیستید"}, status=status.HTTP_400_BAD_REQUEST)
        
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