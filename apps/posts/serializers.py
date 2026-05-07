# apps/posts/serializers.py

from rest_framework import serializers
from .models import Post, Comment, Like
from .models import Post, Comment, Like, SavedPost  
from django.contrib.auth import get_user_model

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_phone = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'user_phone', 'content', 'image',
            'created_at', 'updated_at', 'likes_count', 
            'comments_count', 'is_liked'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else None
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_phone = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'user_phone', 'text', 
            'parent', 'replies', 'replies_count',
            'created_at', 
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at' , 'post']
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else None
    
    def get_replies(self, obj):
        if obj.parent is None:
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def validate(self, attrs):
        parent = attrs.get('parent')
        target_post = self.context.get('target_post')
        post_from_attrs = attrs.get('post')
        
        if parent:
            if target_post and parent.post != target_post:
                raise serializers.ValidationError({
                    "parent": " the parrent should be for comment her "
                })
            
            if parent.parent is not None:
                raise serializers.ValidationError({
                    "parent": " just one reply you can do it "
                })
        
        if target_post and post_from_attrs and post_from_attrs != target_post:
            raise serializers.ValidationError({
                "post": "error"
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    saved_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'post_id', 'saved_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'saved_at']





class SavePostResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    action = serializers.CharField() 
    message = serializers.CharField()
    saved_count = serializers.IntegerField()

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
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
    user = UserMinimalSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'image', 'image_url', 'created_at', 'updated_at',
            'likes_count', 'comments_count', 'is_liked', 'is_saved'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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
        return obj.image.url if obj.image else None


class CommentSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent', 'text', 'created_at', 'replies', 'replies_count']
        read_only_fields = ['id', 'created_at']
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.select_related('user', 'user__profile').order_by('created_at')
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.count() if obj.parent is None else 0