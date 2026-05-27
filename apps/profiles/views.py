
# # apps/profiles/views.py
# from rest_framework import status, permissions
# from rest_framework.response import Response
# from rest_framework.generics import GenericAPIView
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
# from django.db.models import Q

# from .models import Profile
# from .serializers import (
#     ProfileSerializer, ProfileUpdateSerializer, UserProfileSerializer,
#     ProfileSearchQuerySerializer, ProfileUserIdSerializer, 
#     ProfileFollowToggleResponseSerializer, ProfileResponseSerializer,
#     ProfileUpdateResponseSerializer, ProfileFollowListResponseSerializer,
#     ProfileSearchResponseSerializer, ProfileSearchResultSerializer
# )

# User = get_user_model()


# class ProfileView(GenericAPIView):
#     """Get, update or partially update user profile"""
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
    
#     def get_serializer_class(self):
#         if self.request.method in ['PUT', 'PATCH']:
#             return ProfileUpdateSerializer
#         return ProfileSerializer
    
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileSerializer(profile, context={'request': request})
#         return Response({
#             "success": True,
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)
    
#     def put(self, request):
#         profile, created = Profile.objects.get_or_create(user=request.user)
#         serializer = ProfileUpdateSerializer(profile, data=request.data, context={'request': request})
        
#         if serializer.is_valid():
#             serializer.save()
#             profile_serializer = ProfileSerializer(profile, context={'request': request})
#             return Response({
#                 "success": True,
#                 "message": "پروفایل با موفقیت به روز رسانی شد",
#                 "data": profile_serializer.data
#             }, status=status.HTTP_200_OK)
        
#         return Response({
#             "success": False,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
    
#     def patch(self, request):
#         profile, created = Profile.objects.get_or_create(user=request.user)
#         serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True, context={'request': request})
        
#         if serializer.is_valid():
#             serializer.save()
#             profile_serializer = ProfileSerializer(profile, context={'request': request})
#             return Response({
#                 "success": True,
#                 "message": "پروفایل با موفقیت به روز رسانی شد",
#                 "data": profile_serializer.data
#             }, status=status.HTTP_200_OK)
        
#         return Response({
#             "success": False,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


# # class PublicProfileView(GenericAPIView):
# #     """Get public profile of a user by ID"""
# #     permission_classes = [permissions.IsAuthenticated]
# #     serializer_class = ProfileUserIdSerializer
    
# #     def get(self, request, user_id):
# #         serializer = self.get_serializer(data={'user_id': user_id})
# #         serializer.is_valid(raise_exception=True)
        
# #         user = get_object_or_404(User, id=user_id)
# #         profile = get_object_or_404(Profile, user=user)
        
# #         if profile.is_private and not request.user == user:
# #             is_following = profile.followers.filter(id=request.user.id).exists()
# #             if not is_following:
# #                 return Response({
# #                     "success": False,
# #                     "error": "این حساب کاربری خصوصی است"
# #                 }, status=status.HTTP_403_FORBIDDEN)
        
# #         profile_serializer = ProfileSerializer(profile, context={'request': request})
# #         return Response({
# #             "success": True,
# #             "data": profile_serializer.data
# #         }, status=status.HTTP_200_OK)

# class PublicProfileView(GenericAPIView):
#     """Get public profile of a user by ID"""
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request, user_id):
#         # حذف serializer اضافی و مستقیم گرفتن user
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "error": "کاربر یافت نشد"
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             profile = Profile.objects.get(user=user)
#         except Profile.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "error": "پروفایل یافت نشد"
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # بررسی پروفایل خصوصی
#         if profile.is_private and request.user != user:
#             is_following = profile.followers.filter(id=request.user.id).exists()
#             if not is_following:
#                 return Response({
#                     "success": False,
#                     "error": "این حساب کاربری خصوصی است"
#                 }, status=status.HTTP_403_FORBIDDEN)
        
#         # ساخت دیتای پاسخ
#         response_data = {
#             "success": True,
#             "data": {
#                 "id": str(user.id),
#                 "username": user.username,
#                 "display_name": profile.display_name or user.username,
#                 "bio": profile.bio or "",
#                 "profile_image": profile.profile_image.url if profile.profile_image else None,
#                 "posts_count": user.posts.count() if hasattr(user, 'posts') else 0,
#                 "followers_count": profile.followers.count(),
#                 "following_count": profile.following.count(),
#                 "is_following": profile.followers.filter(id=request.user.id).exists(),
#                 "is_private": profile.is_private,
#                 "phone": user.phone if hasattr(user, 'phone') else None
#             }
#         }
        
#         return Response(response_data, status=status.HTTP_200_OK)


# class FollowToggleView(GenericAPIView):
#     """Toggle follow status for a user"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ProfileUserIdSerializer
    
#     def post(self, request, user_id):
#         serializer = self.get_serializer(data={'user_id': user_id})
#         serializer.is_valid(raise_exception=True)
        
#         target_user = get_object_or_404(User, id=user_id)
#         target_profile = get_object_or_404(Profile, user=target_user)
        
#         if request.user == target_user:
#             return Response({
#                 "success": False,
#                 "error": "نمی‌توانید خودتان را دنبال کنید!"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         if target_profile.followers.filter(id=request.user.id).exists():
#             target_profile.followers.remove(request.user)
#             return Response({
#                 "success": True,
#                 "action": "unfollowed",
#                 "message": f"دنبال کردن {target_user.username} لغو شد"
#             }, status=status.HTTP_200_OK)
#         else:
#             target_profile.followers.add(request.user)
#             return Response({
#                 "success": True,
#                 "action": "followed",
#                 "message": f"اکنون {target_user.username} را دنبال می‌کنید"
#             }, status=status.HTTP_200_OK)


# class FollowersListView(GenericAPIView):
#     """Get list of followers for a user"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ProfileUserIdSerializer
    
#     def get(self, request, user_id):
#         serializer = self.get_serializer(data={'user_id': user_id})
#         serializer.is_valid(raise_exception=True)
        
#         user = get_object_or_404(User, id=user_id)
#         profile = get_object_or_404(Profile, user=user)
        
#         followers = profile.followers.select_related('profile').all()
#         followers_data = []
        
#         for follower in followers:
#             follower_profile = Profile.objects.get(user=follower)
#             followers_data.append({
#                 "id": follower.id,
#                 "username": follower.username,
#                 "display_name": follower_profile.display_name,
#                 "profile_image": follower_profile.profile_image.url if follower_profile.profile_image else None,
#                 "phone": follower.phone
#             })
        
#         return Response({
#             "success": True,
#             "count": len(followers_data),
#             "data": followers_data
#         }, status=status.HTTP_200_OK)


# class FollowingListView(GenericAPIView):
#     """Get list of users that a user is following"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ProfileUserIdSerializer
    
#     def get(self, request, user_id):
#         serializer = self.get_serializer(data={'user_id': user_id})
#         serializer.is_valid(raise_exception=True)
        
#         user = get_object_or_404(User, id=user_id)
#         profile = get_object_or_404(Profile, user=user)
        
#         following = profile.following.select_related('profile').all()
#         following_data = []
        
#         for followed in following:
#             followed_profile = Profile.objects.get(user=followed)
#             following_data.append({
#                 "id": followed.id,
#                 "username": followed.username,
#                 "display_name": followed_profile.display_name,
#                 "profile_image": followed_profile.profile_image.url if followed_profile.profile_image else None,
#                 "phone": followed.phone
#             })
        
#         return Response({
#             "success": True,
#             "count": len(following_data),
#             "data": following_data
#         }, status=status.HTTP_200_OK)


# class SearchUserView(GenericAPIView):
#     """Search for users by username or display name"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ProfileSearchQuerySerializer
    
#     def get(self, request):
#         serializer = self.get_serializer(data=request.query_params)
#         serializer.is_valid(raise_exception=True)
        
#         query = serializer.validated_data.get('q', '')
#         limit = serializer.validated_data.get('limit', 20)
        
#         users = User.objects.filter(
#             Q(username__icontains=query) |
#             Q(profile__display_name__icontains=query)
#         ).select_related('profile').distinct()[:limit]
        
#         results = []
#         for user in users:
#             profile = Profile.objects.get(user=user)
#             is_following = profile.followers.filter(id=request.user.id).exists()
#             results.append({
#                 "id": user.id,
#                 "username": user.username,
#                 "display_name": profile.display_name,
#                 "profile_image": profile.profile_image.url if profile.profile_image else None,
#                 "is_private": profile.is_private,
#                 "is_following": is_following
#             })
        
#         return Response({
#             "success": True,
#             "count": len(results),
#             "data": results
#         }, status=status.HTTP_200_OK)


# apps/profiles/views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Profile
from apps.follows.models import Follow 
from .serializers import (
    ProfileSerializer, ProfileUpdateSerializer, ProfileSearchQuerySerializer, ProfileUserIdSerializer, 
    ProfileFollowToggleResponseSerializer, ProfileResponseSerializer,
    ProfileUpdateResponseSerializer, ProfileFollowListResponseSerializer,
    ProfileSearchResponseSerializer, ProfileSearchResultSerializer
)
User = get_user_model()

class ProfileView(GenericAPIView):
    """Get, update or partially update user profile"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProfileUpdateSerializer
        return ProfileSerializer
    
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            profile_serializer = ProfileSerializer(profile, context={'request': request})
            return Response({
                "success": True,
                "message": "پروفایل با موفقیت به روز رسانی شد",
                "data": profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            profile_serializer = ProfileSerializer(profile, context={'request': request})
            return Response({
                "success": True,
                "message": "پروفایل با موفقیت به روز رسانی شد",
                "data": profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PublicProfileView(GenericAPIView):
    """Get public profile of a user by ID"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "کاربر یافت نشد"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({
                "success": False,
                "error": "پروفایل یافت نشد"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # بررسی پروفایل خصوصی
        if profile.is_private and request.user != user:
    
            is_following = Follow.objects.filter(
                follower=request.user, 
                following=user
            ).exists()
            
            if not is_following:
                return Response({
                    "success": False,
                    "error": "این حساب کاربری خصوصی است"
                }, status=status.HTTP_403_FORBIDDEN)
        
        response_data = {
            "success": True,
            "data": {
                "id": str(user.id),
                "username": user.username,
                "display_name": profile.display_name or user.username,
                "bio": profile.bio or "",
                "profile_image": profile.profile_image.url if profile.profile_image else None,
                "posts_count": user.posts.count() if hasattr(user, 'posts') else 0,
                "followers_count": profile.followers_count, # استفاده از property جدید
                "following_count": profile.following_count, # استفاده از property جدید
                "is_following": Follow.objects.filter(
                    follower=request.user, 
                    following=user
                ).exists(),
                "is_private": profile.is_private,
                "phone": user.phone if hasattr(user, 'phone') else None
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class FollowToggleView(GenericAPIView):
    """Toggle follow status for a user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUserIdSerializer
    
    def post(self, request, user_id):
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        
        target_user = get_object_or_404(User, id=user_id)
        
        if request.user == target_user:
            return Response({
                "success": False,
                "error": "نمی‌توانید خودتان را دنبال کنید!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی وضعیت فالو با مدل Follow
        if Follow.objects.filter(
            follower=request.user, 
            following=target_user
        ).exists():
            # آنفالو
            Follow.objects.filter(
                follower=request.user, 
                following=target_user
            ).delete()
            return Response({
                "success": True,
                "action": "unfollowed",
                "message": f"دنبال کردن {target_user.username} لغو شد"
            }, status=status.HTTP_200_OK)
        else:
            # فالو
            Follow.objects.create(
                follower=request.user, 
                following=target_user
            )
            return Response({
                "success": True,
                "action": "followed",
                "message": f"اکنون {target_user.username} را دنبال می‌کنید"
            }, status=status.HTTP_200_OK)

class FollowersListView(GenericAPIView):
    """Get list of followers for a user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUserIdSerializer
    
    def get(self, request, user_id):
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=user_id)
        
        follower_ids = Follow.objects.filter(following=user).values_list('follower', flat=True)
        
        followers = User.objects.filter(id__in=follower_ids).select_related('profile')
        
        followers_data = []
        for follower in followers:
            follower_profile = follower.profile # دسترسی مستقیم از طریق related_name
            followers_data.append({
                "id": follower.id,
                "username": follower.username,
                "display_name": follower_profile.display_name,
                "profile_image": follower_profile.profile_image.url if follower_profile.profile_image else None,
                "phone": getattr(follower, 'phone', None)
            })
        
        return Response({
            "success": True,
            "count": len(followers_data),
            "data": followers_data
        }, status=status.HTTP_200_OK)

class FollowingListView(GenericAPIView):
    """Get list of users that a user is following"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUserIdSerializer
    
    def get(self, request, user_id):
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=user_id)
        # profile = get_object_or_404(Profile, user=user) 
        
        following_ids = Follow.objects.filter(follower=user).values_list('following', flat=True)
        
        following = User.objects.filter(id__in=following_ids).select_related('profile')
        
        following_data = []
        for followed in following:
            followed_profile = followed.profile
            following_data.append({
                "id": followed.id,
                "username": followed.username,
                "display_name": followed_profile.display_name,
                "profile_image": followed_profile.profile_image.url if followed_profile.profile_image else None,
                "phone": getattr(followed, 'phone', None)
            })
        
        return Response({
            "success": True,
            "count": len(following_data),
            "data": following_data
        }, status=status.HTTP_200_OK)

class SearchUserView(GenericAPIView):
    """Search for users by username or display name"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSearchQuerySerializer
    
    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data.get('q', '')
        limit = serializer.validated_data.get('limit', 20)
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__display_name__icontains=query)
        ).select_related('profile').distinct()[:limit]
        
        results = []
        for user in users:
            
            profile = user.profile
            is_following = Follow.objects.filter(
                follower=request.user, 
                following=user
            ).exists()
            results.append({
                "id": user.id,
                "username": user.username,
                "display_name": profile.display_name,
                "profile_image": profile.profile_image.url if profile.profile_image else None,
                "is_private": profile.is_private,
                "is_following": is_following
            })
        
        return Response({
            "success": True,
            "count": len(results),
            "data": results
        }, status=status.HTTP_200_OK)