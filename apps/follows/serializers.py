# apps/follows/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class FollowerSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش فالوورها"""
    id = serializers.UUIDField(source='follower.id', read_only=True)
    username = serializers.CharField(source='follower.username', read_only=True)
    phone = serializers.CharField(source='follower.phone', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'username', 'phone', 'display_name', 'profile_image', 'is_private', 'created_at']

    def get_display_name(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.display_name or obj.follower.username
        return obj.follower.username

    def get_profile_image(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
            return obj.follower.profile.profile_image.url
        return None

    def get_is_private(self, obj):
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.is_private
        return False


class FollowingSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش فالوینگ‌ها"""
    id = serializers.UUIDField(source='following.id', read_only=True)
    username = serializers.CharField(source='following.username', read_only=True)
    phone = serializers.CharField(source='following.phone', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'username', 'phone', 'display_name', 'profile_image', 'is_private', 'created_at']

    def get_display_name(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.display_name or obj.following.username
        return obj.following.username

    def get_profile_image(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
            return obj.following.profile.profile_image.url
        return None

    def get_is_private(self, obj):
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.is_private
        return False


class FollowActionSerializer(serializers.Serializer):
    """سریالایزر برای عملیات فالو/آنفالو"""
    user_id = serializers.UUIDField(required=True)
    
    def validate_user_id(self, value):
        request = self.context.get('request')
        if request and str(request.user.id) == str(value):
            raise serializers.ValidationError("نمی‌توانید خودتان را فالو کنید.")
        return value