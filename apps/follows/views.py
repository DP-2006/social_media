# apps/follows/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Follow
from .serializers import (
    FollowerSerializer, FollowingSerializer, 
    FollowActionSerializer
)

User = get_user_model()


class FollowToggleView(APIView):
    
    #POST /api/follows/toggle/<user_id>/
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        
        # بررسی فالو کردن خود
        if request.user == target_user:
            return Response({
                "success": False,
                "error": "نمی‌توانید خودتان را فالو کنید."
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            follow_exists = Follow.objects.filter(
                follower=request.user, 
                following=target_user
            ).exists()

            if follow_exists:
                # آنفالو کردن
                Follow.objects.filter(
                    follower=request.user, 
                    following=target_user
                ).delete()
                
                # پاک کردن کش
                self._invalidate_cache(request.user.id, target_user.id)
                
                return Response({
                    "success": True,
                    "action": "unfollowed",
                    "message": f"شما {target_user.username} را آنفالو کردید."
                }, status=status.HTTP_200_OK)
            else:
                # فالو کردن
                follow = Follow.objects.create(
                    follower=request.user,
                    following=target_user
                )
                
                # پاک کردن کش
                self._invalidate_cache(request.user.id, target_user.id)
                
                return Response({
                    "success": True,
                    "action": "followed",
                    "message": f"شما اکنون {target_user.username} را فالو می‌کنید.",
                    "data": FollowingSerializer(follow).data
                }, status=status.HTTP_201_CREATED)

    def _invalidate_cache(self, follower_id, following_id):
        """پاک کردن کش مربوط به فالو"""
        cache.delete(f'followers_{following_id}')
        cache.delete(f'following_{follower_id}')
        cache.delete(f'follow_count_{following_id}')
        cache.delete(f'follow_count_{follower_id}')


class FollowersListView(generics.ListAPIView):
    #GET /api/follows/users/<user_id>/followers/
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Follow.objects.filter(following_id=user_id).select_related(
            'follower', 'follower__profile'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "count": queryset.count(),
                "data": serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })


class FollowingListView(generics.ListAPIView):
    #GET /api/follows/users/<user_id>/following/
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Follow.objects.filter(follower_id=user_id).select_related(
            'following', 'following__profile'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "count": queryset.count(),
                "data": serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })


class CheckFollowStatusView(APIView):
    #GET /api/follows/check/?target_id=<user_id>
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        target_id = request.query_params.get('target_id')
        if not target_id:
            return Response({
                "success": False,
                "error": "target_id الزامی است."
            }, status=status.HTTP_400_BAD_REQUEST)

        target_user = get_object_or_404(User, id=target_id)
        
        is_following = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).exists()
        
        is_followed_by = Follow.objects.filter(
            follower=target_user,
            following=request.user
        ).exists()

        return Response({
            "success": True,
            "data": {
                "is_following": is_following,
                "is_followed_by": is_followed_by,
                "is_mutual": is_following and is_followed_by
            }
        })


class FollowCountsView(APIView):
    #GET /api/follows/users/<user_id>/counts/
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        cache_key_followers = f'follow_count_followers_{user_id}'
        cache_key_following = f'follow_count_following_{user_id}'
        
        followers_count = cache.get(cache_key_followers)
        following_count = cache.get(cache_key_following)
        
        if followers_count is None:
            followers_count = Follow.objects.filter(following=user).count()
            cache.set(cache_key_followers, followers_count, 300) 
        
        if following_count is None:
            following_count = Follow.objects.filter(follower=user).count()
            cache.set(cache_key_following, following_count, 300)
        
        return Response({
            "success": True,
            "data": {
                "followers_count": followers_count,
                "following_count": following_count
            }
        })