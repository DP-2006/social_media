from django.shortcuts import render

# Create your views here.
# apps/stories/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Story, StoryView
from .serializers import StorySerializer, StoryViewSerializer
from core.pagination import StandardPagination
from django.db import models

class StoryViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        
        following_ids = self.request.user.following.values_list('following_id', flat=True)
        return Story.objects.filter(
            models.Q(user__in=following_ids) | models.Q(user=self.request.user),
            expires_at__gt=timezone.now() 
        ).select_related('user').order_by('-created_at')

    def perform_create(self, serializer):
        expires_at = timezone.now() + timedelta(hours=24)
        serializer.save(
            user=self.request.user,
            expires_at=expires_at
        )

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        story = self.get_object()
        StoryView.objects.get_or_create(
            story=story,
            viewer=request.user
        )
        return Response({'status': 'viewed'})

    @action(detail=False, methods=['get'])
    def my_stories(self, request):
        stories = Story.objects.filter(user=request.user)
        serializer = self.get_serializer(stories, many=True)
        return Response(serializer.data)


