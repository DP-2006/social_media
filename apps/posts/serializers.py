from rest_framework import serializers
from .models import Post, Comment, Like
from rest_framework.exceptions import PermissionDenied

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


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'image']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


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
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else None
    
    def get_replies(self, obj):
        if obj.parent is None:
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def validate(self, attrs):
        parent_id = attrs.get("parent")
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
                if parent_comment.parent is not None:
                    raise serializers.ValidationError({
                        "parent": "فقط یک سطح کامنت مجاز است"
                    })
                if attrs.get("post") and parent_comment.post != attrs.get("post"):
                    raise serializers.ValidationError({
                        "parent": "کامنت والد باید متعلق به همین پست باشد"
                    })
                attrs['parent'] = parent_comment
            except Comment.DoesNotExist:
                raise serializers.ValidationError({"parent": "کامنت والد یافت نشد"})
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
        
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all()
    
    def perform_update(self, serializer):
        post = self.get_object()
        if post.user != self.request.user:
            raise PermissionDenied("شما فقط می‌توانید پست خودتان را ویرایش کنید")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("شما فقط می‌توانید پست خودتان را حذف کنید")
        instance.delete()