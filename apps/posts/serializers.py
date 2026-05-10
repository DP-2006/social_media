
# # apps/posts/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Post, Comment, Like, SavedPost

# User = get_user_model()


# class UserMinimalSerializer(serializers.ModelSerializer):
#     """Minimal serializer for User model in posts context"""
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


# class PostSerializer(serializers.ModelSerializer):
#     """Serializer for Post model"""
#     user = UserMinimalSerializer(read_only=True)
#     likes_count = serializers.SerializerMethodField()
#     comments_count = serializers.SerializerMethodField()
#     is_liked = serializers.SerializerMethodField()
#     is_saved = serializers.SerializerMethodField()
#     image_url = serializers.SerializerMethodField()
#     share_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Post
#         fields = [
#             'id', 'user', 'content', 'image', 'image_url', 
#             'created_at', 'updated_at', 'likes_count', 
#             'comments_count', 'is_liked', 'is_saved', 'share_count'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']
    
#     def get_likes_count(self, obj):
#         return obj.likes.count()
    
#     def get_comments_count(self, obj):
#         return obj.comments.filter(is_deleted=False).count()
    
#     def get_share_count(self, obj):
#         return getattr(obj, 'share_count', 0)
    
#     def get_is_liked(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             return obj.likes.filter(user=request.user).exists()
#         return False
    
#     def get_is_saved(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             return SavedPost.objects.filter(user=request.user, post=obj).exists()
#         return False
    
#     def get_image_url(self, obj):
#         if obj.image and hasattr(obj.image, 'url'):
#             return obj.image.url
#         return None


# class PostCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating a new post"""
#     class Meta:
#         model = Post
#         fields = ['content', 'image']
#         extra_kwargs = {
#             'content': {'required': False, 'allow_blank': True},
#             'image': {'required': False}
#         }
    
#     def validate(self, data):
#         if not data.get('content') and not data.get('image'):
#             raise serializers.ValidationError("Either content or image is required")
#         if data.get('content') and len(data.get('content')) > 5000:
#             raise serializers.ValidationError("Content cannot exceed 5000 characters")
#         return data


# class PostUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating a post"""
#     class Meta:
#         model = Post
#         fields = ['content', 'image']
#         extra_kwargs = {
#             'content': {'required': False, 'allow_blank': True},
#             'image': {'required': False}
#         }


# class CommentSerializer(serializers.ModelSerializer):
#     """Serializer for Comment model"""
#     user = UserMinimalSerializer(read_only=True)
#     replies = serializers.SerializerMethodField()
#     replies_count = serializers.SerializerMethodField()
#     is_mine = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Comment
#         fields = [
#             'id', 'user', 'post', 'parent', 'text', 
#             'created_at', 'replies', 'replies_count', 'is_mine'
#         ]
#         read_only_fields = ['id', 'created_at', 'post']
    
#     def get_replies(self, obj):
#         if obj.parent is None:
#             replies = obj.replies.filter(is_deleted=False).select_related('user', 'user__profile').order_by('created_at')
#             return CommentSerializer(replies, many=True, context=self.context).data
#         return []
    
#     def get_replies_count(self, obj):
#         return obj.replies.filter(is_deleted=False).count() if obj.parent is None else 0
    
#     def get_is_mine(self, obj):
#         request = self.context.get('request')
#         return request and request.user.is_authenticated and obj.user == request.user


# class CommentCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating a comment"""
#     parent_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID of parent comment for replies")
    
#     class Meta:
#         model = Comment
#         fields = ['text', 'parent_id']
    
#     def validate_text(self, value):
#         if not value or not value.strip():
#             raise serializers.ValidationError("Comment text cannot be empty")
#         if len(value) > 1000:
#             raise serializers.ValidationError("Comment cannot exceed 1000 characters")
#         return value.strip()


# class SavedPostSerializer(serializers.ModelSerializer):
#     """Serializer for SavedPost model"""
#     post = PostSerializer(read_only=True)
#     post_id = serializers.IntegerField(write_only=True, help_text="ID of the post to save")
#     saved_at = serializers.DateTimeField(read_only=True)
    
#     class Meta:
#         model = SavedPost
#         fields = ['id', 'post', 'post_id', 'saved_at', 'created_at']
#         read_only_fields = ['id', 'created_at', 'saved_at']


# class SavedPostListSerializer(serializers.ModelSerializer):
#     """Serializer for saved posts list"""
#     post = PostSerializer(read_only=True)
    
#     class Meta:
#         model = SavedPost
#         fields = ['id', 'post', 'saved_at']


# class LikeSerializer(serializers.ModelSerializer):
#     """Serializer for Like model"""
#     user = UserMinimalSerializer(read_only=True)
    
#     class Meta:
#         model = Like
#         fields = ['id', 'user', 'post', 'created_at']
#         read_only_fields = ['id', 'created_at']


# # ========== Request/Response Serializers ==========
# class PostIdSerializer(serializers.Serializer):
#     """Serializer for post ID validation"""
#     post_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the post"
#     )


# class CommentIdSerializer(serializers.Serializer):
#     """Serializer for comment ID validation"""
#     comment_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the comment"
#     )


# class LikeToggleResponseSerializer(serializers.Serializer):
#     """Serializer for like toggle response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.ChoiceField(choices=['liked', 'unliked'])
#     likes_count = serializers.IntegerField()


# class SavePostResponseSerializer(serializers.Serializer):
#     """Serializer for save post response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.ChoiceField(choices=['saved', 'unsaved'])
#     message = serializers.CharField()
#     saved_count = serializers.IntegerField()


# class CheckSavedStatusResponseSerializer(serializers.Serializer):
#     """Serializer for check saved status response"""
#     success = serializers.BooleanField(default=True)
#     data = serializers.DictField()


# class DeleteCommentResponseSerializer(serializers.Serializer):
#     """Serializer for delete comment response"""
#     success = serializers.BooleanField(default=True)
#     message = serializers.CharField()


# class PostListQuerySerializer(serializers.Serializer):
#     """Serializer for post list query parameters"""
#     limit = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)
#     offset = serializers.IntegerField(required=False, default=0, min_value=0)
#     user_id = serializers.IntegerField(required=False, help_text="Filter posts by user ID")
#     hashtag = serializers.CharField(required=False, help_text="Filter posts by hashtag")


# class ErrorResponseSerializer(serializers.Serializer):
#     """Serializer for error response"""
#     error = serializers.CharField()
#     detail = serializers.CharField(required=False)













# apps/posts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, SavedPost

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for User model in posts context"""
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'profile_image']
    
    def get_display_name(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.display_name or obj.username
        return obj.username
    
    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model - supports file display"""
    user = UserMinimalSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_info = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'image', 'image_url', 
            'file', 'file_url', 'file_info', 'file_name', 'file_size',
            'created_at', 'updated_at', 'likes_count', 
            'comments_count', 'is_liked', 'is_saved', 'share_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_name', 'file_size']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()
    
    def get_share_count(self, obj):
        return getattr(obj, 'share_count', 0)
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedPost.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None
    
    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return obj.file.url
        return None
    
    def get_file_info(self, obj):
        if obj.file:
            return {
                'name': obj.file_name or obj.file.name.split('/')[-1],
                'size': obj.file_size or obj.file.size,
                'size_mb': round((obj.file_size or obj.file.size) / (1024 * 1024), 2),
                'extension': obj.file.name.split('.')[-1].lower() if '.' in obj.file.name else 'unknown'
            }
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new post - supports any file type"""
    
    class Meta:
        model = Post
        fields = ['content', 'image', 'file']
        extra_kwargs = {
            'content': {'required': False, 'allow_blank': True},
            'image': {'required': False},
            'file': {'required': False}
        }
    
    def validate(self, data):
        # حداقل یکی از سه فیلد باید پر باشد
        if not data.get('content') and not data.get('image') and not data.get('file'):
            raise serializers.ValidationError("Either content, image, or file is required")
        
        # اعتبارسنجی محتوا
        if data.get('content') and len(data.get('content')) > 5000:
            raise serializers.ValidationError({"content": "Content cannot exceed 5000 characters"})
        
        # اعتبارسنجی فایل (اختیاری)
        if data.get('file'):
            max_size = 100 * 1024 * 1024  # 100 MB
            if data['file'].size > max_size:
                raise serializers.ValidationError(
                    {"file": f"File size cannot exceed {max_size // (1024 * 1024)} MB"}
                )
        
        return data


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a post - supports any file type"""
    
    class Meta:
        model = Post
        fields = ['content', 'image', 'file']
        extra_kwargs = {
            'content': {'required': False, 'allow_blank': True},
            'image': {'required': False},
            'file': {'required': False}
        }
    
    def validate(self, data):
        if data.get('content') and len(data.get('content')) > 5000:
            raise serializers.ValidationError({"content": "Content cannot exceed 5000 characters"})
        
        if data.get('file'):
            max_size = 100 * 1024 * 1024  # 100 MB
            if data['file'].size > max_size:
                raise serializers.ValidationError(
                    {"file": f"File size cannot exceed {max_size // (1024 * 1024)} MB"}
                )
        
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'post', 'parent', 'text', 
            'created_at', 'replies', 'replies_count', 'is_mine'
        ]
        read_only_fields = ['id', 'created_at', 'post']
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.filter(is_deleted=False).select_related('user', 'user__profile').order_by('created_at')
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.filter(is_deleted=False).count() if obj.parent is None else 0
    
    def get_is_mine(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.user == request.user


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a comment"""
    parent_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID of parent comment for replies")
    
    class Meta:
        model = Comment
        fields = ['text', 'parent_id']
    
    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment cannot exceed 1000 characters")
        return value.strip()


class SavedPostSerializer(serializers.ModelSerializer):
    """Serializer for SavedPost model"""
    post = PostSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True, help_text="ID of the post to save")
    saved_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'post_id', 'saved_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'saved_at']


class SavedPostListSerializer(serializers.ModelSerializer):
    """Serializer for saved posts list"""
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'saved_at']


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']


# ========== Request/Response Serializers ==========
class PostIdSerializer(serializers.Serializer):
    """Serializer for post ID validation"""
    post_id = serializers.IntegerField(
        required=True,
        help_text="ID of the post"
    )


class CommentIdSerializer(serializers.Serializer):
    """Serializer for comment ID validation"""
    comment_id = serializers.IntegerField(
        required=True,
        help_text="ID of the comment"
    )


class LikeToggleResponseSerializer(serializers.Serializer):
    """Serializer for like toggle response"""
    success = serializers.BooleanField(default=True)
    action = serializers.ChoiceField(choices=['liked', 'unliked'])
    likes_count = serializers.IntegerField()


class SavePostResponseSerializer(serializers.Serializer):
    """Serializer for save post response"""
    success = serializers.BooleanField(default=True)
    action = serializers.ChoiceField(choices=['saved', 'unsaved'])
    message = serializers.CharField()
    saved_count = serializers.IntegerField()


class CheckSavedStatusResponseSerializer(serializers.Serializer):
    """Serializer for check saved status response"""
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()


class DeleteCommentResponseSerializer(serializers.Serializer):
    """Serializer for delete comment response"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()


class PostListQuerySerializer(serializers.Serializer):
    """Serializer for post list query parameters"""
    limit = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)
    offset = serializers.IntegerField(required=False, default=0, min_value=0)
    user_id = serializers.IntegerField(required=False, help_text="Filter posts by user ID")
    hashtag = serializers.CharField(required=False, help_text="Filter posts by hashtag")


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error response"""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)