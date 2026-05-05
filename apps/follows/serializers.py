# apps/follows/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class FollowerListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='follower.id', read_only=True)
    username = serializers.CharField(source='follower.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'username', 'display_name', 'profile_image', 'followed_at']
    
    def get_display_name(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.display_name or obj.follower.username
        return obj.follower.username
    
    def get_profile_image(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
            return obj.follower.profile.profile_image.url
        return None


class FollowingListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='following.id', read_only=True)
    username = serializers.CharField(source='following.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'username', 'display_name', 'profile_image', 'followed_at']
    
    def get_display_name(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.display_name or obj.following.username
        return obj.following.username
    
    def get_profile_image(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
            return obj.following.profile.profile_image.url
        return None


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    follower_display_name = serializers.SerializerMethodField()
    following_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Follow
        fields = [
            'id', 'follower', 'following', 
            'follower_username', 'following_username',
            'follower_display_name', 'following_display_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_follower_display_name(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.display_name or obj.follower.username
        return obj.follower.username
    
    def get_following_display_name(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.display_name or obj.following.username
        return obj.following.username