from django.shortcuts import render

# Create your views here.
# apps/messaging/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.pagination import MessagesPagination


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

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None, conversation_pk=None):
        messages = Message.objects.filter(
            conversation_id=conversation_pk,
            sender__not=request.user,
            is_read=False
        )
        messages.update(is_read=True, read_at=timezone.now())
        return Response({'status': 'marked as read'})


from django.db import models
from django.utils import timezone