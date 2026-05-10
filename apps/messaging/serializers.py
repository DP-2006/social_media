# # apps/messaging/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Conversation, Message, GroupConversation, GroupMessage, GroupMember

# User = get_user_model()


# # ========== User Minimal Serializer ==========
# class UserMinimalSerializer(serializers.ModelSerializer):
#     """Minimal serializer for User model"""
#     display_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'display_name', 'profile_image', 'phone']
    
#     def get_display_name(self, obj):
#         if hasattr(obj, 'profile') and obj.profile:
#             return obj.profile.display_name or obj.username
#         return obj.username
    
#     def get_profile_image(self, obj):
#         if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
#             return obj.profile.profile_image.url
#         return None


# # ========== Private Chat Serializers ==========
# class MessageSerializer(serializers.ModelSerializer):
#     """Serializer for Message model"""
#     sender = UserMinimalSerializer(read_only=True)
#     is_mine = serializers.SerializerMethodField()
#     time_ago = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Message
#         fields = ['id', 'sender', 'content', 'created_at', 'is_read', 'read_at', 'is_mine', 'time_ago']
#         read_only_fields = ['id', 'created_at', 'read_at']
    
#     def get_is_mine(self, obj):
#         request = self.context.get('request')
#         return request and obj.sender == request.user
    
#     def get_time_ago(self, obj):
#         from django.utils.timesince import timesince
#         return timesince(obj.created_at)


# class ConversationSerializer(serializers.ModelSerializer):
#     """Serializer for Conversation model"""
#     participants = UserMinimalSerializer(many=True, read_only=True)
#     other_participant = serializers.SerializerMethodField()
#     last_message = serializers.SerializerMethodField()
#     unread_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Conversation
#         fields = [
#             'id', 'participants', 'other_participant', 'last_message',
#             'last_message_at', 'unread_count', 'created_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'last_message_at']
    
#     def get_other_participant(self, obj):
#         request = self.context.get('request')
#         if request:
#             other = obj.participants.exclude(id=request.user.id).first()
#             return UserMinimalSerializer(other).data if other else None
#         return None
    
#     def get_last_message(self, obj):
#         last = obj.messages.order_by('-created_at').first()
#         return MessageSerializer(last, context=self.context).data if last else None
    
#     def get_unread_count(self, obj):
#         request = self.context.get('request')
#         if request:
#             return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
#         return 0


# # ========== Group Chat Serializers ==========
# class GroupMemberSerializer(serializers.ModelSerializer):
#     """Serializer for GroupMember model"""
#     user = UserMinimalSerializer(read_only=True)
#     user_id = serializers.IntegerField(write_only=True, required=False)
#     role_display = serializers.SerializerMethodField()
    
#     class Meta:
#         model = GroupMember
#         fields = ['id', 'user', 'user_id', 'role', 'role_display', 'joined_at', 'is_muted']
#         read_only_fields = ['id', 'joined_at']
    
#     def get_role_display(self, obj):
#         roles = {
#             'admin': 'مدیر',
#             'moderator': 'مدیر انجمن',
#             'member': 'عضو عادی'
#         }
#         return roles.get(obj.role, obj.role)


# class GroupMessageSerializer(serializers.ModelSerializer):
#     """Serializer for GroupMessage model"""
#     sender = UserMinimalSerializer(read_only=True)
#     is_mine = serializers.SerializerMethodField()
#     is_read_by_me = serializers.SerializerMethodField()
#     read_by_count = serializers.SerializerMethodField()
#     read_by_users = serializers.SerializerMethodField()
#     time_ago = serializers.SerializerMethodField()
    
#     class Meta:
#         model = GroupMessage
#         fields = [
#             'id', 'sender', 'content', 'created_at', 'is_read',
#             'is_mine', 'is_read_by_me', 'read_by_count', 'read_by_users', 'time_ago'
#         ]
#         read_only_fields = ['id', 'created_at']
    
#     def get_is_mine(self, obj):
#         request = self.context.get('request')
#         return request and obj.sender == request.user
    
#     def get_is_read_by_me(self, obj):
#         request = self.context.get('request')
#         if request:
#             return obj.read_by.filter(id=request.user.id).exists()
#         return False
    
#     def get_read_by_count(self, obj):
#         return obj.read_by.count()
    
#     def get_read_by_users(self, obj):
#         return UserMinimalSerializer(obj.read_by.all(), many=True).data
    
#     def get_time_ago(self, obj):
#         from django.utils.timesince import timesince
#         return timesince(obj.created_at)


# class GroupConversationSerializer(serializers.ModelSerializer):
#     """Serializer for GroupConversation model"""
#     members = UserMinimalSerializer(many=True, read_only=True)
#     admin = UserMinimalSerializer(read_only=True)
#     member_count = serializers.SerializerMethodField()
#     is_member = serializers.SerializerMethodField()
#     is_admin = serializers.SerializerMethodField()
#     last_message = serializers.SerializerMethodField()
#     unread_count = serializers.SerializerMethodField()
#     my_role = serializers.SerializerMethodField()
    
#     class Meta:
#         model = GroupConversation
#         fields = [
#             'id', 'title', 'avatar', 'description', 'members', 'admin',
#             'member_count', 'is_member', 'is_admin', 'my_role', 'last_message',
#             'last_message_at', 'last_message_preview', 'unread_count', 'is_active',
#             'created_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'last_message_at']
    
#     def get_member_count(self, obj):
#         return obj.members.count()
    
#     def get_is_member(self, obj):
#         request = self.context.get('request')
#         return request and obj.members.filter(id=request.user.id).exists()
    
#     def get_is_admin(self, obj):
#         request = self.context.get('request')
#         return request and obj.admin == request.user
    
#     def get_my_role(self, obj):
#         request = self.context.get('request')
#         if request:
#             member = GroupMember.objects.filter(group=obj, user=request.user).first()
#             if member:
#                 roles = {'admin': 'مدیر', 'moderator': 'مدیر انجمن', 'member': 'عضو عادی'}
#                 return roles.get(member.role, member.role)
#         return None
    
#     def get_last_message(self, obj):
#         last = obj.messages.order_by('-created_at').first()
#         return GroupMessageSerializer(last, context=self.context).data if last else None
    
#     def get_unread_count(self, obj):
#         request = self.context.get('request')
#         if request:
#             return obj.messages.filter(is_read=False).exclude(read_by=request.user).count()
#         return 0


# class CreateGroupSerializer(serializers.ModelSerializer):
#     """Serializer for creating a new group"""
#     member_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         write_only=True,
#         required=False,
#         help_text="List of user IDs to add as members"
#     )
    
#     class Meta:
#         model = GroupConversation
#         fields = ['title', 'avatar', 'description', 'member_ids']
    
#     def validate_title(self, value):
#         if not value or not value.strip():
#             raise serializers.ValidationError("Group title is required")
#         if len(value) > 100:
#             raise serializers.ValidationError("Group title cannot exceed 100 characters")
#         return value.strip()
    
#     def create(self, validated_data):
#         member_ids = validated_data.pop('member_ids', [])
#         request = self.context.get('request')
        
#         group = GroupConversation.objects.create(
#             **validated_data,
#             admin=request.user
#         )
        
#         # Add members
#         group.members.add(request.user)  # Creator
#         for member_id in member_ids:
#             if member_id != request.user.id:
#                 group.members.add(member_id)
        
#         # Create GroupMember records
#         for member in group.members.all():
#             role = 'admin' if member == request.user else 'member'
#             GroupMember.objects.create(group=group, user=member, role=role)
        
#         return group


# class AddMemberToGroupSerializer(serializers.Serializer):
#     """Serializer for adding members to a group"""
#     user_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         required=True,
#         help_text="List of user IDs to add to the group"
#     )
#     group_id = serializers.IntegerField(
#         required=False,
#         write_only=True,
#         help_text="ID of the group (can be passed in URL)"
#     )
    
#     def validate_user_ids(self, value):
#         if not value:
#             raise serializers.ValidationError("At least one user ID is required")
#         if len(value) > 50:
#             raise serializers.ValidationError("Cannot add more than 50 users at once")
#         return value


# # ========== Request/Response Serializers ==========
# class StartConversationSerializer(serializers.Serializer):
#     """Serializer for starting a conversation"""
#     target_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to start conversation with"
#     )


# class TargetAnalysisSerializer(serializers.Serializer):
#     """Serializer for target user analysis"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user to analyze"
#     )


# class OpeningMessageSuggestionsSerializer(serializers.Serializer):
#     """Serializer for opening message suggestions"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the target user"
#     )
#     count = serializers.IntegerField(
#         required=False,
#         default=3,
#         min_value=1,
#         max_value=5,
#         help_text="Number of suggestions to return"
#     )


# class ReplySuggestionSerializer(serializers.Serializer):
#     """Serializer for reply suggestions"""
#     last_message = serializers.CharField(
#         required=True,
#         max_length=500,
#         help_text="Last message content"
#     )


# class IceBreakerTopicsSerializer(serializers.Serializer):
#     """Serializer for icebreaker topics"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the target user"
#     )


# class ConversationIdSerializer(serializers.Serializer):
#     """Serializer for conversation ID validation"""
#     conversation_id = serializers.IntegerField(required=True)


# class GroupDetailSerializer(serializers.Serializer):
#     """Serializer for group detail operations"""
#     group_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the group"
#     )


# class MemberActionSerializer(serializers.Serializer):
#     """Serializer for member actions (add/remove)"""
#     group_id = serializers.IntegerField(required=True)
#     user_id = serializers.IntegerField(required=True)


# class LeaveGroupSerializer(serializers.Serializer):
#     """Serializer for leaving a group"""
#     group_id = serializers.IntegerField(required=True)


# class MarkReadSerializer(serializers.Serializer):
#     """Serializer for marking messages as read"""
#     message_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         required=False,
#         help_text="List of message IDs to mark as read"
#     )
#     mark_all = serializers.BooleanField(
#         required=False,
#         default=False,
#         help_text="Mark all messages as read"
#     )






from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, GroupConversation, GroupMessage, GroupMember

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for User model"""
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'profile_image', 'phone']
    
    def get_display_name(self, obj) -> str:
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.display_name or obj.username
        return obj.username
    
    def get_profile_image(self, obj) -> str | None:
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserMinimalSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'is_read', 'read_at', 'is_mine', 'time_ago']
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_is_mine(self, obj) -> bool:
        request = self.context.get('request')
        return request and obj.sender == request.user
    
    def get_time_ago(self, obj) -> str:
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    participants = UserMinimalSerializer(many=True, read_only=True)
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'other_participant', 'last_message',
            'last_message_at', 'unread_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']
    
    def get_other_participant(self, obj) -> dict | None:
        request = self.context.get('request')
        if request:
            other = obj.participants.exclude(id=request.user.id).first()
            return UserMinimalSerializer(other).data if other else None
        return None
    
    def get_last_message(self, obj) -> dict | None:
        last = obj.messages.order_by('-created_at').first()
        return MessageSerializer(last, context=self.context).data if last else None
    
    def get_unread_count(self, obj) -> int:
        request = self.context.get('request')
        if request:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class GroupMemberSerializer(serializers.ModelSerializer):
    """Serializer for GroupMember model"""
    user = UserMinimalSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'user_id', 'role', 'role_display', 'joined_at', 'is_muted']
        read_only_fields = ['id', 'joined_at']
    
    def get_role_display(self, obj) -> str:
        roles = {
            'admin': 'مدیر',
            'moderator': 'مدیر انجمن',
            'member': 'عضو عادی'
        }
        return roles.get(obj.role, obj.role)


class GroupMessageSerializer(serializers.ModelSerializer):
    """Serializer for GroupMessage model"""
    sender = UserMinimalSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()
    is_read_by_me = serializers.SerializerMethodField()
    read_by_count = serializers.SerializerMethodField()
    read_by_users = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupMessage
        fields = [
            'id', 'sender', 'content', 'created_at', 'is_read',
            'is_mine', 'is_read_by_me', 'read_by_count', 'read_by_users', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_mine(self, obj) -> bool:
        request = self.context.get('request')
        return request and obj.sender == request.user
    
    def get_is_read_by_me(self, obj) -> bool:
        request = self.context.get('request')
        if request:
            return obj.read_by.filter(id=request.user.id).exists()
        return False
    
    def get_read_by_count(self, obj) -> int:
        return obj.read_by.count()
    
    def get_read_by_users(self, obj) -> list:
        return UserMinimalSerializer(obj.read_by.all(), many=True).data
    
    def get_time_ago(self, obj) -> str:
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class GroupConversationSerializer(serializers.ModelSerializer):
    """Serializer for GroupConversation model"""
    members = UserMinimalSerializer(many=True, read_only=True)
    admin = UserMinimalSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupConversation
        fields = [
            'id', 'title', 'avatar', 'description', 'members', 'admin',
            'member_count', 'is_member', 'is_admin', 'my_role', 'last_message',
            'last_message_at', 'last_message_preview', 'unread_count', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']
    
    def get_member_count(self, obj) -> int:
        return obj.members.count()
    
    def get_is_member(self, obj) -> bool:
        request = self.context.get('request')
        return request and obj.members.filter(id=request.user.id).exists()
    
    def get_is_admin(self, obj) -> bool:
        request = self.context.get('request')
        return request and obj.admin == request.user
    
    def get_my_role(self, obj) -> str | None:
        request = self.context.get('request')
        if request:
            member = GroupMember.objects.filter(group=obj, user=request.user).first()
            if member:
                roles = {'admin': 'مدیر', 'moderator': 'مدیر انجمن', 'member': 'عضو عادی'}
                return roles.get(member.role, member.role)
        return None
    
    def get_last_message(self, obj) -> dict | None:
        last = obj.messages.order_by('-created_at').first()
        return GroupMessageSerializer(last, context=self.context).data if last else None
    
    def get_unread_count(self, obj) -> int:
        request = self.context.get('request')
        if request:
            return obj.messages.filter(is_read=False).exclude(read_by=request.user).count()
        return 0


class CreateGroupSerializer(serializers.ModelSerializer):
    """Serializer for creating a new group"""
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of user IDs to add as members"
    )
    
    class Meta:
        model = GroupConversation
        fields = ['title', 'avatar', 'description', 'member_ids']
    
    def validate_title(self, value) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Group title is required")
        if len(value) > 100:
            raise serializers.ValidationError("Group title cannot exceed 100 characters")
        return value.strip()
    
    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        request = self.context.get('request')
        
        group = GroupConversation.objects.create(
            **validated_data,
            admin=request.user
        )
        
        # Add members
        group.members.add(request.user)  # Creator
        for member_id in member_ids:
            if member_id != request.user.id:
                group.members.add(member_id)
        
        # Create GroupMember records
        for member in group.members.all():
            role = 'admin' if member == request.user else 'member'
            GroupMember.objects.create(group=group, user=member, role=role)
        
        return group


class AddMemberToGroupSerializer(serializers.Serializer):
    """Serializer for adding members to a group"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of user IDs to add to the group"
    )
    group_id = serializers.IntegerField(
        required=False,
        write_only=True,
        help_text="ID of the group (can be passed in URL)"
    )
    
    def validate_user_ids(self, value) -> list:
        if not value:
            raise serializers.ValidationError("At least one user ID is required")
        if len(value) > 50:
            raise serializers.ValidationError("Cannot add more than 50 users at once")
        return value


class StartConversationSerializer(serializers.Serializer):
    """Serializer for starting a conversation"""
    target_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to start conversation with"
    )


class TargetAnalysisSerializer(serializers.Serializer):
    """Serializer for target user analysis"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user to analyze"
    )


class OpeningMessageSuggestionsSerializer(serializers.Serializer):
    """Serializer for opening message suggestions"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the target user"
    )
    count = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=5,
        help_text="Number of suggestions to return"
    )


class ReplySuggestionSerializer(serializers.Serializer):
    """Serializer for reply suggestions"""
    last_message = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Last message content"
    )


class IceBreakerTopicsSerializer(serializers.Serializer):
    """Serializer for icebreaker topics"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the target user"
    )


class ConversationIdSerializer(serializers.Serializer):
    """Serializer for conversation ID validation"""
    conversation_id = serializers.IntegerField(required=True)


class GroupDetailSerializer(serializers.Serializer):
    """Serializer for group detail operations"""
    group_id = serializers.IntegerField(
        required=True,
        help_text="ID of the group"
    )


class MemberActionSerializer(serializers.Serializer):
    """Serializer for member actions (add/remove)"""
    group_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)


class LeaveGroupSerializer(serializers.Serializer):
    """Serializer for leaving a group"""
    group_id = serializers.IntegerField(required=True)


class MarkReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read"""
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of message IDs to mark as read"
    )
    mark_all = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Mark all messages as read"
    )