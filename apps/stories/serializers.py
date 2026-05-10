# # apps/stories/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from .models import Story, StoryView

# User = get_user_model()


# class UserMinimalForStorySerializer(serializers.ModelSerializer):
#     """Minimal serializer for User in stories context"""
#     display_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'display_name', 'profile_image']
    
#     def get_display_name(self, obj):
#         if hasattr(obj, 'profile') and obj.profile:
#             return obj.profile.display_name or obj.username
#         return obj.username
    
#     def get_profile_image(self, obj):
#         if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
#             return obj.profile.profile_image.url
#         return None


# class StorySerializer(serializers.ModelSerializer):
#     """Serializer for Story model"""
#     user = UserMinimalForStorySerializer(read_only=True)
#     views_count = serializers.SerializerMethodField()
#     is_viewed = serializers.SerializerMethodField()
#     is_expired = serializers.SerializerMethodField()
#     remaining_hours = serializers.SerializerMethodField()
#     image_url = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Story
#         fields = [
#             'id', 'user', 'image', 'image_url', 'caption', 
#             'views_count', 'is_viewed', 'is_expired', 'remaining_hours',
#             'created_at', 'expires_at'
#         ]
#         read_only_fields = ['id', 'user', 'created_at', 'expires_at']
    
#     def get_views_count(self, obj):
#         return obj.views.count()
    
#     def get_is_viewed(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             return obj.views.filter(viewer=request.user).exists()
#         return False
    
#     def get_is_expired(self, obj):
#         return obj.expires_at <= timezone.now()
    
#     def get_remaining_hours(self, obj):
#         if obj.expires_at > timezone.now():
#             delta = obj.expires_at - timezone.now()
#             return round(delta.total_seconds() / 3600, 1)
#         return 0
    
#     def get_image_url(self, obj):
#         if obj.image and hasattr(obj.image, 'url'):
#             return obj.image.url
#         return None


# class StoryCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating a new story"""
#     class Meta:
#         model = Story
#         fields = ['image', 'caption']
#         extra_kwargs = {
#             'image': {'required': True},
#             'caption': {'required': False, 'allow_blank': True}
#         }
    
#     def validate_caption(self, value):
#         if value and len(value) > 500:
#             raise serializers.ValidationError("Caption cannot exceed 500 characters")
#         return value
    
#     def validate_image(self, value):
#         if not value:
#             raise serializers.ValidationError("Image is required for story")
#         return value


# class StoryViewSerializer(serializers.ModelSerializer):
#     """Serializer for StoryView model"""
#     viewer = UserMinimalForStorySerializer(read_only=True)
#     viewer_id = serializers.IntegerField(write_only=True, required=False)
#     viewer_username = serializers.CharField(source='viewer.username', read_only=True)
    
#     class Meta:
#         model = StoryView
#         fields = ['id', 'story', 'viewer', 'viewer_id', 'viewer_username', 'created_at']
#         read_only_fields = ['id', 'viewer', 'created_at']


# class StoryViewerSerializer(serializers.ModelSerializer):
#     """Serializer for viewers of a story"""
#     viewer = UserMinimalForStorySerializer(read_only=True)
#     viewed_at = serializers.DateTimeField(source='created_at', read_only=True)
    
#     class Meta:
#         model = StoryView
#         fields = ['id', 'viewer', 'viewed_at']


# # ========== Request/Response Serializers ==========
# class StoryIdSerializer(serializers.Serializer):
#     """Serializer for story ID validation"""
#     story_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the story"
#     )


# class StoryViewResponseSerializer(serializers.Serializer):
#     """Serializer for story view response"""
#     status = serializers.CharField(default="viewed")
#     success = serializers.BooleanField(default=True)


# class StoryListQuerySerializer(serializers.Serializer):
#     """Serializer for story list query parameters"""
#     limit = serializers.IntegerField(
#         required=False,
#         default=20,
#         min_value=1,
#         max_value=50,
#         help_text="Number of stories to return"
#     )
#     offset = serializers.IntegerField(
#         required=False,
#         default=0,
#         min_value=0,
#         help_text="Number of stories to skip"
#     )
#     include_expired = serializers.BooleanField(
#         required=False,
#         default=False,
#         help_text="Include expired stories"
#     )


# class StoryDeleteResponseSerializer(serializers.Serializer):
#     """Serializer for story delete response"""
#     success = serializers.BooleanField(default=True)
#     message = serializers.CharField()


# class MyStoriesResponseSerializer(serializers.Serializer):
#     """Serializer for my stories response"""
#     success = serializers.BooleanField(default=True)
#     data = StorySerializer(many=True)
#     count = serializers.IntegerField()


# class ActiveStoriesResponseSerializer(serializers.Serializer):
#     """Serializer for active stories response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = StorySerializer(many=True)


# class StoryViewersResponseSerializer(serializers.Serializer):
#     """Serializer for story viewers response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = StoryViewerSerializer(many=True)


# class ErrorResponseSerializer(serializers.Serializer):
#     """Serializer for error response"""
#     success = serializers.BooleanField(default=False)
#     error = serializers.CharField()
#     detail = serializers.CharField(required=False)






from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Story, StoryView

User = get_user_model()


class StoryUserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for User in stories context"""
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'profile_image']
    
    def get_display_name(self, obj) -> str:
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.display_name or obj.username
        return obj.username
    
    def get_profile_image(self, obj) -> str | None:
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None


class StorySerializer(serializers.ModelSerializer):
    """Serializer for Story model"""
    user = StoryUserMinimalSerializer(read_only=True)
    views_count = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    remaining_hours = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id', 'user', 'image', 'image_url', 'caption', 
            'views_count', 'is_viewed', 'is_expired', 'remaining_hours',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'expires_at']
    
    def get_views_count(self, obj) -> int:
        return obj.views.count()
    
    def get_is_viewed(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.views.filter(viewer=request.user).exists()
        return False
    
    def get_is_expired(self, obj) -> bool:
        return obj.expires_at <= timezone.now()
    
    def get_remaining_hours(self, obj) -> float:
        if obj.expires_at > timezone.now():
            delta = obj.expires_at - timezone.now()
            return round(delta.total_seconds() / 3600, 1)
        return 0
    
    def get_image_url(self, obj) -> str | None:
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None


class StoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new story"""
    class Meta:
        model = Story
        fields = ['image', 'caption']
        extra_kwargs = {
            'image': {'required': True},
            'caption': {'required': False, 'allow_blank': True}
        }
    
    def validate_caption(self, value) -> str:
        if value and len(value) > 500:
            raise serializers.ValidationError("Caption cannot exceed 500 characters")
        return value
    
    def validate_image(self, value) -> str:
        if not value:
            raise serializers.ValidationError("Image is required for story")
        return value


class StoryViewSerializer(serializers.ModelSerializer):
    """Serializer for StoryView model"""
    viewer = StoryUserMinimalSerializer(read_only=True)
    viewer_id = serializers.IntegerField(write_only=True, required=False)
    viewer_username = serializers.CharField(source='viewer.username', read_only=True)
    
    class Meta:
        model = StoryView
        fields = ['id', 'story', 'viewer', 'viewer_id', 'viewer_username', 'created_at']
        read_only_fields = ['id', 'viewer', 'created_at']


class StoryViewerSerializer(serializers.ModelSerializer):
    """Serializer for viewers of a story"""
    viewer = StoryUserMinimalSerializer(read_only=True)
    viewed_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = StoryView
        fields = ['id', 'viewer', 'viewed_at']


# ========== Request/Response Serializers ==========
class StoryIdSerializer(serializers.Serializer):
    """Serializer for story ID validation"""
    story_id = serializers.IntegerField(
        required=True,
        help_text="ID of the story"
    )


class StoryViewResponseSerializer(serializers.Serializer):
    """Serializer for story view response"""
    status = serializers.CharField(default="viewed")
    success = serializers.BooleanField(default=True)


class StoryListQuerySerializer(serializers.Serializer):
    """Serializer for story list query parameters"""
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=50,
        help_text="Number of stories to return"
    )
    offset = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        help_text="Number of stories to skip"
    )
    include_expired = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Include expired stories"
    )


class StoryDeleteResponseSerializer(serializers.Serializer):
    """Serializer for story delete response"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()


class MyStoriesResponseSerializer(serializers.Serializer):
    """Serializer for my stories response"""
    success = serializers.BooleanField(default=True)
    data = StorySerializer(many=True)
    count = serializers.IntegerField()


class ActiveStoriesResponseSerializer(serializers.Serializer):
    """Serializer for active stories response"""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = StorySerializer(many=True)


class StoryViewersResponseSerializer(serializers.Serializer):
    """Serializer for story viewers response"""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = StoryViewerSerializer(many=True)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error response"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    detail = serializers.CharField(required=False)