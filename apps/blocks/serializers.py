# # apps/blocks/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Block

# User = get_user_model()


# class BlockSerializer(serializers.ModelSerializer):
#     """Serializer for Block model"""
#     blocker_username = serializers.CharField(source='blocker.username', read_only=True)
#     blocked_username = serializers.CharField(source='blocked.username', read_only=True)
#     blocked_phone = serializers.CharField(source='blocked.phone', read_only=True)
#     blocker_id = serializers.IntegerField(source='blocker.id', read_only=True)
#     blocked_id = serializers.IntegerField(source='blocked.id', read_only=True)
    
#     class Meta:
#         model = Block
#         fields = [
#             'id', 'blocker', 'blocker_id', 'blocker_username',
#             'blocked', 'blocked_id', 'blocked_username', 'blocked_phone',
#             'reason', 'created_at'
#         ]
#         read_only_fields = ['id', 'created_at']


# class BlockedUserSerializer(serializers.ModelSerializer):
#     """Serializer for blocked users list"""
#     blocked_at = serializers.DateTimeField(source='blocked_info.created_at', read_only=True)
#     block_reason = serializers.CharField(source='blocked_info.reason', read_only=True)
#     display_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = User
#         fields = [
#             'id', 'username', 'phone', 'display_name', 
#             'profile_image', 'blocked_at', 'block_reason'
#         ]
    
#     def get_display_name(self, obj):
#         if hasattr(obj, 'profile') and obj.profile:
#             return obj.profile.display_name or obj.username
#         return obj.username
    
#     def get_profile_image(self, obj):
#         if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
#             return obj.profile.profile_image.url
#         return None


# class BlockRequestSerializer(serializers.Serializer):
#     """Serializer for block request"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to block/unblock"
#     )
#     reason = serializers.CharField(
#         max_length=255,
#         required=False,
#         allow_blank=True,
#         help_text="Reason for blocking (optional)"
#     )


# class BlockUserSerializer(serializers.Serializer):
#     """Serializer for block_user action"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to block"
#     )
#     reason = serializers.CharField(
#         max_length=255,
#         required=False,
#         allow_blank=True,
#         help_text="Reason for blocking"
#     )


# class UnblockUserSerializer(serializers.Serializer):
#     """Serializer for unblock_user action"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to unblock"
#     )


# class ToggleBlockSerializer(serializers.Serializer):
#     """Serializer for toggle_block action"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to toggle block"
#     )
#     reason = serializers.CharField(
#         max_length=255,
#         required=False,
#         allow_blank=True,
#         help_text="Reason for blocking (only used when blocking)"
#     )


# class CheckBlockSerializer(serializers.Serializer):
#     """Serializer for check_block action"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to check block status with"
#     )


# class BlockResponseSerializer(serializers.Serializer):
#     """Serializer for block response"""
#     status = serializers.CharField()
#     message = serializers.CharField()
#     blocked_user = serializers.DictField(required=False)


# class CheckBlockResponseSerializer(serializers.Serializer):
#     """Serializer for check block response"""
#     user_id = serializers.IntegerField()
#     username = serializers.CharField()
#     is_blocked = serializers.BooleanField()
#     is_blocked_by = serializers.BooleanField()
#     can_interact = serializers.BooleanField()
















from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Block

User = get_user_model()


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for Block model"""
    blocker_username = serializers.CharField(source='blocker.username', read_only=True)
    blocked_username = serializers.CharField(source='blocked.username', read_only=True)
    blocked_phone = serializers.CharField(source='blocked.phone', read_only=True)
    blocker_id = serializers.IntegerField(source='blocker.id', read_only=True)
    blocked_id = serializers.IntegerField(source='blocked.id', read_only=True)
    
    class Meta:
        model = Block
        fields = [
            'id', 'blocker', 'blocker_id', 'blocker_username',
            'blocked', 'blocked_id', 'blocked_username', 'blocked_phone',
            'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BlockedUserSerializer(serializers.ModelSerializer):
    """Serializer for blocked users list"""
    blocked_at = serializers.DateTimeField(source='blocked_info.created_at', read_only=True)
    block_reason = serializers.CharField(source='blocked_info.reason', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'display_name', 
            'profile_image', 'blocked_at', 'block_reason'
        ]
    
    def get_display_name(self, obj) -> str:
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.display_name or obj.username
        return obj.username
    
    def get_profile_image(self, obj) -> str | None:
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None


class BlockRequestSerializer(serializers.Serializer):
    """Serializer for block request"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to block/unblock"
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Reason for blocking (optional)"
    )


class BlockUserSerializer(serializers.Serializer):
    """Serializer for block_user action"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to block"
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Reason for blocking"
    )


class UnblockUserSerializer(serializers.Serializer):
    """Serializer for unblock_user action"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to unblock"
    )


class ToggleBlockSerializer(serializers.Serializer):
    """Serializer for toggle_block action"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to toggle block"
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Reason for blocking (only used when blocking)"
    )


class CheckBlockSerializer(serializers.Serializer):
    """Serializer for check_block action"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to check block status with"
    )


class BlockResponseSerializer(serializers.Serializer):
    """Serializer for block response"""
    status = serializers.CharField()
    message = serializers.CharField()
    blocked_user = serializers.DictField(required=False)


class CheckBlockResponseSerializer(serializers.Serializer):
    """Serializer for check block response"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    is_blocked = serializers.BooleanField()
    is_blocked_by = serializers.BooleanField()
    can_interact = serializers.BooleanField()