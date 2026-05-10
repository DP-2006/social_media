# # apps/follows/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Follow

# User = get_user_model()


# class UserIdSerializer(serializers.Serializer):
#     """Serializer for validating user_id"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user"
#     )


# class FollowerListSerializer(serializers.ModelSerializer):
#     """Serializer for list of followers"""
#     id = serializers.IntegerField(source='follower.id', read_only=True)
#     username = serializers.CharField(source='follower.username', read_only=True)
#     display_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
#     followed_at = serializers.DateTimeField(source='created_at', read_only=True)
#     phone = serializers.CharField(source='follower.phone', read_only=True)
    
#     class Meta:
#         model = Follow
#         fields = ['id', 'username', 'display_name', 'profile_image', 'phone', 'followed_at']
    
#     def get_display_name(self, obj):
#         if hasattr(obj.follower, 'profile') and obj.follower.profile:
#             return obj.follower.profile.display_name or obj.follower.username
#         return obj.follower.username
    
#     def get_profile_image(self, obj):
#         if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
#             return obj.follower.profile.profile_image.url
#         return None


# class FollowingListSerializer(serializers.ModelSerializer):
#     """Serializer for list of users being followed"""
#     id = serializers.IntegerField(source='following.id', read_only=True)
#     username = serializers.CharField(source='following.username', read_only=True)
#     display_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
#     followed_at = serializers.DateTimeField(source='created_at', read_only=True)
#     phone = serializers.CharField(source='following.phone', read_only=True)
    
#     class Meta:
#         model = Follow
#         fields = ['id', 'username', 'display_name', 'profile_image', 'phone', 'followed_at']
    
#     def get_display_name(self, obj):
#         if hasattr(obj.following, 'profile') and obj.following.profile:
#             return obj.following.profile.display_name or obj.following.username
#         return obj.following.username
    
#     def get_profile_image(self, obj):
#         if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
#             return obj.following.profile.profile_image.url
#         return None


# class FollowSerializer(serializers.ModelSerializer):
#     """Serializer for Follow model"""
#     follower_username = serializers.CharField(source='follower.username', read_only=True)
#     following_username = serializers.CharField(source='following.username', read_only=True)
#     follower_display_name = serializers.SerializerMethodField()
#     following_display_name = serializers.SerializerMethodField()
#     follower_profile_image = serializers.SerializerMethodField()
#     following_profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Follow
#         fields = [
#             'id', 'follower', 'following', 
#             'follower_username', 'following_username',
#             'follower_display_name', 'following_display_name',
#             'follower_profile_image', 'following_profile_image',
#             'created_at'
#         ]
#         read_only_fields = ['id', 'created_at']
    
#     def get_follower_display_name(self, obj):
#         if hasattr(obj.follower, 'profile') and obj.follower.profile:
#             return obj.follower.profile.display_name or obj.follower.username
#         return obj.follower.username
    
#     def get_following_display_name(self, obj):
#         if hasattr(obj.following, 'profile') and obj.following.profile:
#             return obj.following.profile.display_name or obj.following.username
#         return obj.following.username
    
#     def get_follower_profile_image(self, obj):
#         if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
#             return obj.follower.profile.profile_image.url
#         return None
    
#     def get_following_profile_image(self, obj):
#         if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
#             return obj.following.profile.profile_image.url
#         return None


# class FollowCountSerializer(serializers.Serializer):
#     """Serializer for follow counts response"""
#     followers_count = serializers.IntegerField()
#     following_count = serializers.IntegerField()


# class FollowToggleSerializer(serializers.Serializer):
#     """Serializer for follow toggle response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.CharField()
#     message = serializers.CharField()


# class FollowResponseSerializer(serializers.Serializer):
#     """Serializer for follow/unfollow response"""
#     success = serializers.BooleanField()
#     message = serializers.CharField()
#     error = serializers.CharField(required=False)


# class FollowersListResponseSerializer(serializers.Serializer):
#     """Serializer for followers list response"""
#     success = serializers.BooleanField()
#     count = serializers.IntegerField()
#     data = serializers.ListField(child=serializers.DictField())


# class FollowRequestSerializer(serializers.Serializer):
#     """Serializer for follow request"""
#     user_id = serializers.IntegerField(required=True, help_text="ID of the user to follow/unfollow")




from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class UserIdSerializer(serializers.Serializer):
    """Serializer for validating user_id"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user"
    )


class FollowerListSerializer(serializers.ModelSerializer):
    """Serializer for list of followers"""
    id = serializers.IntegerField(source='follower.id', read_only=True)
    username = serializers.CharField(source='follower.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    phone = serializers.CharField(source='follower.phone', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'username', 'display_name', 'profile_image', 'phone', 'followed_at']
    
    def get_display_name(self, obj) -> str:
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.display_name or obj.follower.username
        return obj.follower.username
    
    def get_profile_image(self, obj) -> str | None:
        if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
            return obj.follower.profile.profile_image.url
        return None


class FollowingListSerializer(serializers.ModelSerializer):
    """Serializer for list of users being followed"""
    id = serializers.IntegerField(source='following.id', read_only=True)
    username = serializers.CharField(source='following.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    phone = serializers.CharField(source='following.phone', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'username', 'display_name', 'profile_image', 'phone', 'followed_at']
    
    def get_display_name(self, obj) -> str:
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.display_name or obj.following.username
        return obj.following.username
    
    def get_profile_image(self, obj) -> str | None:
        if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
            return obj.following.profile.profile_image.url
        return None


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    follower_display_name = serializers.SerializerMethodField()
    following_display_name = serializers.SerializerMethodField()
    follower_profile_image = serializers.SerializerMethodField()
    following_profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Follow
        fields = [
            'id', 'follower', 'following', 
            'follower_username', 'following_username',
            'follower_display_name', 'following_display_name',
            'follower_profile_image', 'following_profile_image',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_follower_display_name(self, obj) -> str:
        if hasattr(obj.follower, 'profile') and obj.follower.profile:
            return obj.follower.profile.display_name or obj.follower.username
        return obj.follower.username
    
    def get_following_display_name(self, obj) -> str:
        if hasattr(obj.following, 'profile') and obj.following.profile:
            return obj.following.profile.display_name or obj.following.username
        return obj.following.username
    
    def get_follower_profile_image(self, obj) -> str | None:
        if hasattr(obj.follower, 'profile') and obj.follower.profile and obj.follower.profile.profile_image:
            return obj.follower.profile.profile_image.url
        return None
    
    def get_following_profile_image(self, obj) -> str | None:
        if hasattr(obj.following, 'profile') and obj.following.profile and obj.following.profile.profile_image:
            return obj.following.profile.profile_image.url
        return None


class FollowCountSerializer(serializers.Serializer):
    """Serializer for follow counts response"""
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()


class FollowToggleSerializer(serializers.Serializer):
    """Serializer for follow toggle response"""
    success = serializers.BooleanField(default=True)
    action = serializers.CharField()
    message = serializers.CharField()


class FollowResponseSerializer(serializers.Serializer):
    """Serializer for follow/unfollow response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    error = serializers.CharField(required=False)


class FollowersListResponseSerializer(serializers.Serializer):
    """Serializer for followers list response"""
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    data = serializers.ListField(child=serializers.DictField())


class FollowRequestSerializer(serializers.Serializer):
    """Serializer for follow request"""
    user_id = serializers.IntegerField(required=True, help_text="ID of the user to follow/unfollow")