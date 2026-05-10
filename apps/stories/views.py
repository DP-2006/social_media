# # apps/stories/views.py
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
# from django.utils import timezone
# from datetime import timedelta
# from django.db import models

# from .models import Story, StoryView
# from .serializers import (
#     StorySerializer, StoryCreateSerializer, StoryViewSerializer,
#     StoryViewerSerializer, StoryIdSerializer, StoryViewResponseSerializer,
#     StoryListQuerySerializer, StoryDeleteResponseSerializer,
#     MyStoriesResponseSerializer, ActiveStoriesResponseSerializer,
#     StoryViewersResponseSerializer
# )
# from core.pagination import StandardPagination


# class StoryViewSet(GenericViewSet, 
#                     ListModelMixin, 
#                     CreateModelMixin, 
#                     RetrieveModelMixin, 
#                     DestroyModelMixin):
#     """
#     ViewSet for managing stories
    
#     Provides endpoints for:
#     - Listing active stories from followed users
#     - Creating new stories
#     - Viewing story details
#     - Deleting own stories
#     - Marking stories as viewed
#     - Getting user's own stories
#     """
#     permission_classes = [IsAuthenticated]
#     pagination_class = StandardPagination
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return StoryCreateSerializer
#         return StorySerializer
    
#     def get_queryset(self):
#         """Get active stories from followed users and self"""
#         following_ids = self.request.user.following.values_list('following_id', flat=True)
#         return Story.objects.filter(
#             models.Q(user__in=following_ids) | models.Q(user=self.request.user),
#             expires_at__gt=timezone.now()
#         ).select_related('user', 'user__profile').order_by('-created_at')
    
#     def perform_create(self, serializer):
#         expires_at = timezone.now() + timedelta(hours=24)
#         serializer.save(
#             user=self.request.user,
#             expires_at=expires_at
#         )
    
#     @action(detail=True, methods=['post'], url_path='view')
#     def view_story(self, request, pk=None):
#         """
#         Mark a story as viewed by the current user
        
#         POST: Records that the current user has viewed this story
#         """
#         story = self.get_object()
        
#         # Don't count user's own views
#         if story.user == request.user:
#             return Response({
#                 "success": False,
#                 "error": "You cannot view your own story"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         view, created = StoryView.objects.get_or_create(
#             story=story,
#             viewer=request.user
#         )
        
#         return Response({
#             'status': 'viewed',
#             'success': True
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['get'], url_path='my-stories')
#     def my_stories(self, request):
#         """
#         Get all stories created by the current user
        
#         GET: Returns list of user's own stories (including expired)
#         """
#         stories = Story.objects.filter(user=request.user).order_by('-created_at')
#         serializer = self.get_serializer(stories, many=True, context={'request': request})
        
#         return Response({
#             "success": True,
#             "data": serializer.data,
#             "count": len(serializer.data)
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=True, methods=['get'], url_path='viewers')
#     def story_viewers(self, request, pk=None):
#         """
#         Get list of users who viewed a story
        
#         GET: Returns list of viewers for the story (only for story owner)
#         """
#         story = self.get_object()
        
#         # Only story owner can see viewers
#         if story.user != request.user:
#             return Response({
#                 "success": False,
#                 "error": "You don't have permission to view viewers of this story"
#             }, status=status.HTTP_403_FORBIDDEN)
        
#         viewers = StoryView.objects.filter(story=story).select_related('viewer', 'viewer__profile').order_by('-created_at')
#         serializer = StoryViewerSerializer(viewers, many=True)
        
#         return Response({
#             "success": True,
#             "count": len(serializer.data),
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['get'], url_path='active')
#     def active_stories(self, request):
#         """
#         Get all active (not expired) stories from followed users
        
#         GET: Returns list of active stories
#         """
#         following_ids = request.user.following.values_list('following_id', flat=True)
        
#         # Get active stories
#         active_stories = Story.objects.filter(
#             models.Q(user__in=following_ids) | models.Q(user=request.user),
#             expires_at__gt=timezone.now()
#         ).select_related('user', 'user__profile').order_by('-created_at')
        
#         # Group by user
#         stories_by_user = {}
#         for story in active_stories:
#             user_id = story.user.id
#             if user_id not in stories_by_user:
#                 stories_by_user[user_id] = {
#                     'user': story.user,
#                     'stories': []
#                 }
#             stories_by_user[user_id]['stories'].append(story)
        
#         serializer = self.get_serializer(active_stories, many=True, context={'request': request})
        
#         return Response({
#             "success": True,
#             "count": len(serializer.data),
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['get'], url_path='status')
#     def stories_status(self, request):
#         """
#         Get stories status for followed users
        
#         GET: Returns count of active stories per user
#         """
#         following_ids = request.user.following.values_list('following_id', flat=True)
        
#         # Count active stories per user
#         stories_count = Story.objects.filter(
#             user__in=following_ids,
#             expires_at__gt=timezone.now()
#         ).values('user_id').annotate(count=models.Count('id'))
        
#         # Get last story time per user
#         last_stories = Story.objects.filter(
#             user__in=following_ids,
#             expires_at__gt=timezone.now()
#         ).values('user_id').annotate(last_story_time=models.Max('created_at'))
        
#         result = []
#         for user_id in following_ids:
#             story_data = {
#                 'user_id': user_id,
#                 'has_story': False,
#                 'story_count': 0,
#                 'last_story_time': None
#             }
            
#             for count_item in stories_count:
#                 if count_item['user_id'] == user_id:
#                     story_data['has_story'] = True
#                     story_data['story_count'] = count_item['count']
#                     break
            
#             for last_item in last_stories:
#                 if last_item['user_id'] == user_id:
#                     story_data['last_story_time'] = last_item['last_story_time']
#                     break
            
#             result.append(story_data)
        
#         return Response({
#             "success": True,
#             "data": result
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=True, methods=['delete'], url_path='delete')
#     def delete_story(self, request, pk=None):
#         """
#         Delete a story (soft delete or hard delete)
        
#         DELETE: Removes the story (only owner can delete)
#         """
#         story = self.get_object()
        
#         if story.user != request.user:
#             return Response({
#                 "success": False,
#                 "error": "You don't have permission to delete this story"
#             }, status=status.HTTP_403_FORBIDDEN)
        
#         story.delete()
        
#         return Response({
#             "success": True,
#             "message": "Story deleted successfully"
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=True, methods=['get'], url_path='has-viewed')
#     def has_viewed(self, request, pk=None):
#         """
#         Check if current user has viewed a story
        
#         GET: Returns whether the user has viewed this story
#         """
#         story = self.get_object()
        
#         has_viewed = StoryView.objects.filter(
#             story=story,
#             viewer=request.user
#         ).exists()
        
#         return Response({
#             "success": True,
#             "data": {
#                 "has_viewed": has_viewed,
#                 "story_id": story.id
#             }
#         }, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['get'], url_path='unviewed-stories')
#     def unviewed_stories(self, request):
#         """
#         Get stories that current user hasn't viewed yet
        
#         GET: Returns list of unviewed stories from followed users
#         """
#         following_ids = request.user.following.values_list('following_id', flat=True)
        
#         # Get viewed story IDs for this user
#         viewed_story_ids = StoryView.objects.filter(
#             viewer=request.user
#         ).values_list('story_id', flat=True)
        
#         # Get unviewed stories
#         unviewed_stories = Story.objects.filter(
#             models.Q(user__in=following_ids) | models.Q(user=request.user),
#             expires_at__gt=timezone.now()
#         ).exclude(
#             id__in=viewed_story_ids
#         ).exclude(
#             user=request.user  # Don't show user's own stories as unviewed
#         ).select_related('user', 'user__profile').order_by('-created_at')
        
#         serializer = self.get_serializer(unviewed_stories, many=True, context={'request': request})
        
#         return Response({
#             "success": True,
#             "count": len(serializer.data),
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)














# apps/stories/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django.utils import timezone
from datetime import timedelta
from django.db import models

from .models import Story, StoryView
from .serializers import (
    StorySerializer, StoryCreateSerializer, StoryViewSerializer,
    StoryViewerSerializer, StoryIdSerializer, StoryViewResponseSerializer,
    StoryListQuerySerializer, StoryDeleteResponseSerializer,
    MyStoriesResponseSerializer, ActiveStoriesResponseSerializer,
    StoryViewersResponseSerializer
)
from core.pagination import StandardPagination


class StoryViewSet(GenericViewSet, 
                    ListModelMixin, 
                    CreateModelMixin, 
                    RetrieveModelMixin, 
                    DestroyModelMixin):
    """
    ViewSet for managing stories
    
    Provides endpoints for:
    - Listing active stories from followed users
    - Creating new stories
    - Viewing story details
    - Deleting own stories
    - Marking stories as viewed
    - Getting user's own stories
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StoryCreateSerializer
        return StorySerializer
    
    def get_queryset(self):
        """Get active stories from followed users and self"""
        following_ids = self.request.user.following_set.values_list('following_id', flat=True)
        return Story.objects.filter(
            models.Q(user__in=following_ids) | models.Q(user=self.request.user),
            expires_at__gt=timezone.now()
        ).select_related('user', 'user__profile').order_by('-created_at')
    
    def perform_create(self, serializer):
        expires_at = timezone.now() + timedelta(hours=24)
        serializer.save(
            user=self.request.user,
            expires_at=expires_at
        )
    
    @action(detail=True, methods=['post'], url_path='view')
    def view_story(self, request, pk=None):
        """
        Mark a story as viewed by the current user
        
        POST: Records that the current user has viewed this story
        """
        story = self.get_object()
        
        # Don't count user's own views
        if story.user == request.user:
            return Response({
                "success": False,
                "error": "You cannot view your own story"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        view, created = StoryView.objects.get_or_create(
            story=story,
            viewer=request.user
        )
        
        return Response({
            'status': 'viewed',
            'success': True
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='my-stories')
    def my_stories(self, request):
        """
        Get all stories created by the current user
        
        GET: Returns list of user's own stories (including expired)
        """
        stories = Story.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(stories, many=True, context={'request': request})
        
        return Response({
            "success": True,
            "data": serializer.data,
            "count": len(serializer.data)
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='viewers')
    def story_viewers(self, request, pk=None):
        """
        Get list of users who viewed a story
        
        GET: Returns list of viewers for the story (only for story owner)
        """
        story = self.get_object()
        
        # Only story owner can see viewers
        if story.user != request.user:
            return Response({
                "success": False,
                "error": "You don't have permission to view viewers of this story"
            }, status=status.HTTP_403_FORBIDDEN)
        
        viewers = StoryView.objects.filter(story=story).select_related('viewer', 'viewer__profile').order_by('-created_at')
        serializer = StoryViewerSerializer(viewers, many=True)
        
        return Response({
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='active')
    def active_stories(self, request):
        """
        Get all active (not expired) stories from followed users
        
        GET: Returns list of active stories
        """
        following_ids = request.user.following_set.values_list('following_id', flat=True)
        
        # Get active stories
        active_stories = Story.objects.filter(
            models.Q(user__in=following_ids) | models.Q(user=request.user),
            expires_at__gt=timezone.now()
        ).select_related('user', 'user__profile').order_by('-created_at')
        
        # Group by user
        stories_by_user = {}
        for story in active_stories:
            user_id = story.user.id
            if user_id not in stories_by_user:
                stories_by_user[user_id] = {
                    'user': story.user,
                    'stories': []
                }
            stories_by_user[user_id]['stories'].append(story)
        
        serializer = self.get_serializer(active_stories, many=True, context={'request': request})
        
        return Response({
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='status')
    def stories_status(self, request):
        """
        Get stories status for followed users
        
        GET: Returns count of active stories per user
        """
        following_ids = request.user.following_set.values_list('following_id', flat=True)
        
        # Count active stories per user
        stories_count = Story.objects.filter(
            user__in=following_ids,
            expires_at__gt=timezone.now()
        ).values('user_id').annotate(count=models.Count('id'))
        
        # Get last story time per user
        last_stories = Story.objects.filter(
            user__in=following_ids,
            expires_at__gt=timezone.now()
        ).values('user_id').annotate(last_story_time=models.Max('created_at'))
        
        result = []
        for user_id in following_ids:
            story_data = {
                'user_id': user_id,
                'has_story': False,
                'story_count': 0,
                'last_story_time': None
            }
            
            for count_item in stories_count:
                if count_item['user_id'] == user_id:
                    story_data['has_story'] = True
                    story_data['story_count'] = count_item['count']
                    break
            
            for last_item in last_stories:
                if last_item['user_id'] == user_id:
                    story_data['last_story_time'] = last_item['last_story_time']
                    break
            
            result.append(story_data)
        
        return Response({
            "success": True,
            "data": result
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_story(self, request, pk=None):
        """
        Delete a story (soft delete or hard delete)
        
        DELETE: Removes the story (only owner can delete)
        """
        story = self.get_object()
        
        if story.user != request.user:
            return Response({
                "success": False,
                "error": "You don't have permission to delete this story"
            }, status=status.HTTP_403_FORBIDDEN)
        
        story.delete()
        
        return Response({
            "success": True,
            "message": "Story deleted successfully"
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='has-viewed')
    def has_viewed(self, request, pk=None):
        """
        Check if current user has viewed a story
        
        GET: Returns whether the user has viewed this story
        """
        story = self.get_object()
        
        has_viewed = StoryView.objects.filter(
            story=story,
            viewer=request.user
        ).exists()
        
        return Response({
            "success": True,
            "data": {
                "has_viewed": has_viewed,
                "story_id": story.id
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='unviewed-stories')
    def unviewed_stories(self, request):
        """
        Get stories that current user hasn't viewed yet
        
        GET: Returns list of unviewed stories from followed users
        """
        following_ids = request.user.following_set.values_list('following_id', flat=True)
        
        # Get viewed story IDs for this user
        viewed_story_ids = StoryView.objects.filter(
            viewer=request.user
        ).values_list('story_id', flat=True)
        
        # Get unviewed stories
        unviewed_stories = Story.objects.filter(
            models.Q(user__in=following_ids) | models.Q(user=request.user),
            expires_at__gt=timezone.now()
        ).exclude(
            id__in=viewed_story_ids
        ).exclude(
            user=request.user  # Don't show user's own stories as unviewed
        ).select_related('user', 'user__profile').order_by('-created_at')
        
        serializer = self.get_serializer(unviewed_stories, many=True, context={'request': request})
        
        return Response({
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        }, status=status.HTTP_200_OK)