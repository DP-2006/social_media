# # apps/hashtags/serializers.py
# from rest_framework import serializers
# from .models import Hashtag, PostHashtag


# class HashtagSerializer(serializers.ModelSerializer):
#     """Serializer for Hashtag model"""
#     post_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Hashtag
#         fields = ['id', 'name', 'usage_count', 'created_at', 'post_count']
#         read_only_fields = ['id', 'usage_count', 'created_at']
    
#     def get_post_count(self, obj):
#         return PostHashtag.objects.filter(hashtag=obj).count()


# class TrendingHashtagSerializer(serializers.ModelSerializer):
#     """Serializer for trending hashtags"""
#     rank = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Hashtag
#         fields = ['id', 'name', 'usage_count', 'rank']
    
#     def get_rank(self, obj):
#         # This will be set in the view
#         return getattr(obj, 'rank', None)


# class HashtagSearchSerializer(serializers.Serializer):
#     """Serializer for hashtag search parameters"""
#     q = serializers.CharField(
#         required=False,
#         allow_blank=True,
#         max_length=100,
#         help_text="Search query for hashtag name"
#     )
#     limit = serializers.IntegerField(
#         required=False,
#         default=20,
#         min_value=1,
#         max_value=100,
#         help_text="Maximum number of results to return"
#     )


# class HashtagPostsSerializer(serializers.Serializer):
#     """Serializer for hashtag posts response"""
#     hashtag_name = serializers.CharField()
#     post_count = serializers.IntegerField()
#     posts = serializers.ListField(child=serializers.DictField(), required=False)


# class HashtagStatsSerializer(serializers.Serializer):
#     """Serializer for hashtag statistics"""
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     usage_count = serializers.IntegerField()
#     post_count = serializers.IntegerField()
#     created_at = serializers.DateTimeField()


# class HashtagCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating new hashtags"""
#     class Meta:
#         model = Hashtag
#         fields = ['name']
    
#     def validate_name(self, value):
#         """Validate hashtag name format"""
#         if not value.startswith('#'):
#             value = f'#{value}'
        
#         if ' ' in value:
#             raise serializers.ValidationError("Hashtag name cannot contain spaces")
        
#         if not value[1:].isalnum() and not all(c.isalnum() or c == '_' for c in value[1:]):
#             raise serializers.ValidationError("Hashtag can only contain letters, numbers, and underscores")
        
#         return value.lower()


# class PostHashtagSerializer(serializers.ModelSerializer):
#     """Serializer for PostHashtag model"""
#     hashtag_name = serializers.CharField(source='hashtag.name', read_only=True)
#     hashtag_usage_count = serializers.IntegerField(source='hashtag.usage_count', read_only=True)
    
#     class Meta:
#         model = PostHashtag
#         fields = ['id', 'post', 'hashtag', 'hashtag_name', 'hashtag_usage_count', 'created_at']
#         read_only_fields = ['id', 'created_at']


# class BulkHashtagSerializer(serializers.Serializer):
#     """Serializer for bulk hashtag operations"""
#     hashtags = serializers.ListField(
#         child=serializers.CharField(max_length=100),
#         help_text="List of hashtag names"
#     )
    
#     def validate_hashtags(self, value):
#         if not value:
#             raise serializers.ValidationError("At least one hashtag is required")
        
#         # Remove duplicates and empty strings
#         cleaned = list(set([h.strip().lower() for h in value if h.strip()]))
        
#         if len(cleaned) > 30:
#             raise serializers.ValidationError("Maximum 30 hashtags allowed")
        
#         return cleaned


# class HashtagSuggestResponseSerializer(serializers.Serializer):
#     """Serializer for hashtag suggestions response"""
#     success = serializers.BooleanField()
#     data = HashtagSerializer(many=True)










from rest_framework import serializers
from .models import Hashtag, PostHashtag


class HashtagSerializer(serializers.ModelSerializer):
    """Serializer for Hashtag model"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'usage_count', 'created_at', 'post_count']
        read_only_fields = ['id', 'usage_count', 'created_at']
    
    def get_post_count(self, obj) -> int:
        return PostHashtag.objects.filter(hashtag=obj).count()


class TrendingHashtagSerializer(serializers.ModelSerializer):
    """Serializer for trending hashtags"""
    rank = serializers.SerializerMethodField()
    
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'usage_count', 'rank']
    
    def get_rank(self, obj) -> int | None:
        return getattr(obj, 'rank', None)


class HashtagSearchSerializer(serializers.Serializer):
    """Serializer for hashtag search parameters"""
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text="Search query for hashtag name"
    )
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=100,
        help_text="Maximum number of results to return"
    )


class HashtagPostsSerializer(serializers.Serializer):
    """Serializer for hashtag posts response"""
    hashtag_name = serializers.CharField()
    post_count = serializers.IntegerField()
    posts = serializers.ListField(child=serializers.DictField(), required=False)


class HashtagStatsSerializer(serializers.Serializer):
    """Serializer for hashtag statistics"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    usage_count = serializers.IntegerField()
    post_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class HashtagCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new hashtags"""
    class Meta:
        model = Hashtag
        fields = ['name']
    
    def validate_name(self, value) -> str:
        if not value.startswith('#'):
            value = f'#{value}'
        
        if ' ' in value:
            raise serializers.ValidationError("Hashtag name cannot contain spaces")
        
        if not value[1:].isalnum() and not all(c.isalnum() or c == '_' for c in value[1:]):
            raise serializers.ValidationError("Hashtag can only contain letters, numbers, and underscores")
        
        return value.lower()


class PostHashtagSerializer(serializers.ModelSerializer):
    """Serializer for PostHashtag model"""
    hashtag_name = serializers.CharField(source='hashtag.name', read_only=True)
    hashtag_usage_count = serializers.IntegerField(source='hashtag.usage_count', read_only=True)
    
    class Meta:
        model = PostHashtag
        fields = ['id', 'post', 'hashtag', 'hashtag_name', 'hashtag_usage_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class BulkHashtagSerializer(serializers.Serializer):
    """Serializer for bulk hashtag operations"""
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text="List of hashtag names"
    )
    
    def validate_hashtags(self, value) -> list:
        if not value:
            raise serializers.ValidationError("At least one hashtag is required")
        
        cleaned = list(set([h.strip().lower() for h in value if h.strip()]))
        
        if len(cleaned) > 30:
            raise serializers.ValidationError("Maximum 30 hashtags allowed")
        
        return cleaned


class HashtagSuggestResponseSerializer(serializers.Serializer):
    """Serializer for hashtag suggestions response"""
    success = serializers.BooleanField()
    data = HashtagSerializer(many=True)