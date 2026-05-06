# apps/follows/views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Follow
from .serializers import FollowSerializer, FollowerListSerializer
from apps.blocks.views import BlockedUsersMixin

User = get_user_model()



class FollowersListView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        follows = Follow.objects.filter(
            following=user
        ).select_related('follower', 'follower__profile')
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        follows = follows.exclude(follower_id__in=blocked_ids)
        follows = follows.order_by('-created_at')
        
        results = []
        for follow in follows:
            follower = follow.follower
            profile = getattr(follower, 'profile', None)
            results.append({
                "id": str(follower.id),
                "username": follower.username,
                "display_name": profile.display_name if profile else follower.username,
                "profile_image": profile.profile_image.url if profile and profile.profile_image else None,
                "followed_at": follow.created_at
            })
        
        return Response({
            "success": True,
            "count": len(results),
            "data": results
        }, status=status.HTTP_200_OK)



class FollowingListView(generics.ListAPIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerListSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        follows = Follow.objects.select_related('following').filter(
            follower_id=user_id
        ).only('id', 'created_at', 'following__id', 'following__username', 'following__email')
        
        blocked_ids = self.get_mutually_blocked_ids(self.request.user)
        follows = follows.exclude(following_id__in=blocked_ids)
        
        return follows



class FollowUserView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        follower = request.user
        following = get_object_or_404(User, id=user_id)
        
        if follower.id == following.id:
            return Response(
                {'error': 'نمی‌توانید خودتان را فالو کنید!'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if following.id in blocked_ids:
            return Response({
                "success": False,
                "error": "نمی‌توانید این کاربر را فالو کنید (بلاک شده)"
            }, status=status.HTTP_403_FORBIDDEN)
        
        follow, created = Follow.objects.get_or_create(
            follower=follower,
            following=following
        )
        
        if created:
            return Response(
                {'success': True, 'message': f'شما {following.username} را فالو کردید'}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'success': False, 'message': 'شما قبلاً این کاربر را فالو کرده‌اید'}, 
            status=status.HTTP_200_OK
        )



class UnfollowUserView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        deleted_count, _ = Follow.objects.filter(
            follower=request.user,
            following_id=user_id
        ).delete()
        
        if deleted_count > 0:
            return Response(
                {'success': True, 'message': 'با موفقیت آنفالو کردید'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'success': False, 'error': 'شما این کاربر را فالو نکرده‌اید'}, 
            status=status.HTTP_400_BAD_REQUEST
        )



class FollowToggleView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        
        if request.user == target_user:
            return Response({
                "success": False,
                "error": "نمی‌توانید خودتان را فالو کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        if target_user.id in blocked_ids:
            return Response({
                "success": False,
                "error": "نمی‌توانید این کاربر را فالو کنید (بلاک شده)"
            }, status=status.HTTP_403_FORBIDDEN)
        
        follow = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).first()
        
        if follow:
            follow.delete()
            return Response({
                "success": True,
                "action": "unfollowed",
                "message": f"شما {target_user.username} را آنفالو کردید"
            }, status=status.HTTP_200_OK)
        else:
            follow = Follow.objects.create(
                follower=request.user,
                following=target_user
            )
            return Response({
                "success": True,
                "action": "followed",
                "message": f"شما اکنون {target_user.username} را فالو می‌کنید"
            }, status=status.HTTP_201_CREATED)


class FollowCountView(APIView, BlockedUsersMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        blocked_ids = self.get_mutually_blocked_ids(request.user)
        
        followers_count = Follow.objects.filter(
            following=user
        ).exclude(
            follower_id__in=blocked_ids
        ).count()
        
        following_count = Follow.objects.filter(
            follower=user
        ).exclude(
            following_id__in=blocked_ids
        ).count()
        
        return Response({
            "success": True,
            "data": {
                "followers_count": followers_count,
                "following_count": following_count
            }
        }, status=status.HTTP_200_OK)