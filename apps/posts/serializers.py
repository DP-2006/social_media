# apps/posts/serializers.py

from rest_framework import serializers
from .models import Post, Comment, Like


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