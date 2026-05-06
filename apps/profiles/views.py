from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer, UserProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

User = get_user_model()

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        serializer = ProfileUpdateSerializer(
            profile, 
            data=request.data,
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "the profilr has sucsses fuly update it ",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        serializer = ProfileUpdateSerializer(
            profile, 
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "sucssefuly update profile ",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PublicProfileView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=user)
        
        if profile.is_private and not request.user == user:
            is_following = profile.followers.filter(id=request.user.id).exists()
            if not is_following:
                return Response({
                    "success": False,
                    "error": "this private account "
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProfileSerializer(profile)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class FollowToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        target_profile = get_object_or_404(Profile, user=target_user)
        
        if request.user == target_user:
            return Response({
                "success": False,
                "error": "YOU CAB T FOLLOW HER!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if target_profile.followers.filter(id=request.user.id).exists():
            target_profile.followers.remove(request.user)
            return Response({
                "success": True,
                "action": "unfollowed",
                "message": f"folling{target_user.username} canceleed "
            }, status=status.HTTP_200_OK)
        else:
            target_profile.followers.add(request.user)
            return Response({
                "success": True,
                "action": "followed",
                "message": f"now following {target_user.username}"
            }, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=user)
        
        followers = profile.followers.all()
        followers_data = []
        # N + 1 proplem query error not performansing code 
        for follower in followers:
            follower_profile = Profile.objects.get(user=follower)
            followers_data.append({
                "id": follower.id,
                "username": follower.username,
                "display_name": follower_profile.display_name,
                "avatar": follower_profile.avatar.url if follower_profile.avatar else None
            })
        
        return Response({
            "success": True,
            "count": len(followers_data),
            "data": followers_data
        }, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=user)
        
        following = profile.following.all()
        following_data = []
        
        for followed in following:
            followed_profile = Profile.objects.get(user=followed)
            following_data.append({
                "id": followed.id,
                "username": followed.username,
                "display_name": followed_profile.display_name,
                "avatar": followed_profile.avatar.url if followed_profile.avatar else None
            })
        
        return Response({
            "success": True,
            "count": len(following_data),
            "data": following_data
        }, status=status.HTTP_200_OK)


class SearchUserView(APIView):
    #GET /api/profiles/search/?q=username
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({
                "success": False,
                "error": "plese enter ypu pramt "
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(username__icontains=query)[:20]
        
        results = []
        for user in users:
            profile = Profile.objects.get(user=user)
            results.append({
                "id": user.id,
                "username": user.username,
                "display_name": profile.display_name,
                "avatar": profile.avatar.url if profile.avatar else None,
                "is_private": profile.is_private
            })
        
        return Response({
            "success": True,
            "count": len(results),
            "data": results
        }, status=status.HTTP_200_OK)