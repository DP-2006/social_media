# apps/search/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class SearchQuerySerializer(serializers.Serializer):
    """Base serializer for search query parameters"""
    q = serializers.CharField(
        required=True,
        min_length=1,
        max_length=200,
        help_text="Search query string"
    )
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=50,
        help_text="Maximum number of results to return"
    )
    offset = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        help_text="Number of results to skip for pagination"
    )
    
    def validate_q(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Search query cannot be empty")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Search query must be at least 2 characters")
        return value.strip()


class GlobalSearchQuerySerializer(SearchQuerySerializer):
    """Serializer for global search query parameters"""
    force_simple = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Force using simple search instead of AI-powered search"
    )


class SearchPostsQuerySerializer(SearchQuerySerializer):
    use_ollama = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Whether to use Ollama AI for keyword extraction"
    )


class SearchByUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        min_length=1,
        max_length=150,
        help_text="Username to search for (with or without @ prefix)"
    )
    
    def validate_username(self, value):
        value = value.strip()
        if value.startswith('@'):
            value = value[1:]
        if not value:
            raise serializers.ValidationError("Username cannot be empty")
        return value


class SearchUsersQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        help_text="Search query for username or display name"
    )
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=50,
        help_text="Maximum number of results to return"
    )


class SearchHashtagsQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        help_text="Search query for hashtag"
    )
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=50,
        help_text="Maximum number of results to return"
    )


class SearchSuggestionsQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        help_text="Search query for suggestions"
    )
    limit = serializers.IntegerField(
        required=False,
        default=10,
        min_value=1,
        max_value=20,
        help_text="Maximum number of suggestions to return"
    )


class UserSearchSerializer(serializers.Serializer):
    id = serializers.UUIDField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    display_name = serializers.CharField(allow_blank=True, allow_null=True, help_text="Display name")
    profile_image = serializers.CharField(allow_null=True, help_text="Profile image URL")
    bio = serializers.CharField(allow_blank=True, allow_null=True, help_text="User bio")
    is_private = serializers.BooleanField(default=False, help_text="Whether account is private")
    is_following = serializers.BooleanField(default=False, help_text="Whether current user follows this user")
    followers_count = serializers.IntegerField(default=0, help_text="Number of followers")
    can_view = serializers.BooleanField(default=True, help_text="Whether current user can view this profile")
    phone = serializers.CharField(allow_null=True, required=False, help_text="Phone number")


class HashtagSearchSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Hashtag name (without #)")
    usage_count = serializers.IntegerField(help_text="Number of times hashtag has been used")
    url = serializers.SerializerMethodField(help_text="URL to hashtag page")
    
    def get_url(self, obj):
        if isinstance(obj, dict):
            name = obj.get('name', '')
        else:
            name = obj.name
        return f"/api/hashtags/{name}/"


class PostSearchSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    content = serializers.CharField(allow_blank=True)
    image_url = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    user = UserSearchSerializer()
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    score = serializers.FloatField(required=False, help_text="Relevance score")


class SearchResultSerializer(serializers.Serializer):
    query = serializers.CharField(help_text="Original search query")
    source = serializers.CharField(help_text="Search engine used (ollama/simple)")
    smart_keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[],
        help_text="AI-extracted keywords from query"
    )
    users = UserSearchSerializer(many=True, help_text="User search results")
    hashtags = HashtagSearchSerializer(many=True, help_text="Hashtag search results")
    posts = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[],
        help_text="Post search results"
    )
    total_count = serializers.IntegerField(required=False, help_text="Total number of results")
    has_next = serializers.BooleanField(required=False, help_text="Whether more results are available")


class SearchSuggestionUserSerializer(serializers.Serializer):
    type = serializers.CharField(default="user", help_text="Result type")
    text = serializers.CharField(help_text="Username")
    display = serializers.CharField(help_text="Display name or username")
    image = serializers.CharField(allow_null=True, help_text="Profile image URL")
    id = serializers.UUIDField(help_text="User ID")


class SearchSuggestionHashtagSerializer(serializers.Serializer):
    type = serializers.CharField(default="hashtag", help_text="Result type")
    text = serializers.CharField(help_text="Hashtag text (with #)")
    count = serializers.IntegerField(help_text="Usage count")
    name = serializers.CharField(help_text="Hashtag name without #")


class SearchSuggestionsSerializer(serializers.Serializer):
    users = SearchSuggestionUserSerializer(many=True, help_text="User suggestions")
    hashtags = SearchSuggestionHashtagSerializer(many=True, help_text="Hashtag suggestions")


class SearchConfigSerializer(serializers.Serializer):
    use_ollama = serializers.BooleanField(help_text="Whether Ollama AI search is enabled")
    ollama_timeout = serializers.IntegerField(help_text="Ollama request timeout in seconds")
    ollama_model = serializers.CharField(
        required=False,
        help_text="Ollama model name"
    )
    min_query_length = serializers.IntegerField(
        required=False,
        default=2,
        help_text="Minimum query length for search"
    )
    max_results_per_page = serializers.IntegerField(
        required=False,
        default=50,
        help_text="Maximum results per page"
    )


class UsersSearchResponseSerializer(serializers.Serializer):
    """Serializer for users search response"""
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()


class HashtagsSearchResponseSerializer(serializers.Serializer):
    """Serializer for hashtags search response"""
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()


class PostsSearchResponseSerializer(serializers.Serializer):
    """Serializer for posts search response"""
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()


class GlobalSearchResponseSerializer(serializers.Serializer):
    """Serializer for global search response"""
    success = serializers.BooleanField(default=True)
    data = SearchResultSerializer()


class SearchSuggestionsResponseSerializer(serializers.Serializer):
    """Serializer for search suggestions response"""
    success = serializers.BooleanField(default=True)
    data = SearchSuggestionsSerializer()


class SearchConfigResponseSerializer(serializers.Serializer):
    """Serializer for search config response"""
    success = serializers.BooleanField(default=True)
    data = SearchConfigSerializer()


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error response"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    detail = serializers.CharField(required=False)