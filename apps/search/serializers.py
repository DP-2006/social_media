# apps/search/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSearchSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    display_name = serializers.CharField(allow_blank=True, allow_null=True)
    profile_image = serializers.CharField(allow_null=True)
    bio = serializers.CharField(allow_blank=True, allow_null=True)
    is_private = serializers.BooleanField(default=False)
    is_following = serializers.BooleanField(default=False)
    followers_count = serializers.IntegerField(default=0)
    can_view = serializers.BooleanField(default=True)


class HashtagSearchSerializer(serializers.Serializer):
    name = serializers.CharField()
    usage_count = serializers.IntegerField()

    def get_url(self, obj):
        if isinstance(obj, dict):
            return f"/hashtag/{obj.get('name', '')}"
        return f"/hashtag/{obj.name}"


class SearchResultSerializer(serializers.Serializer):
    query = serializers.CharField()
    source = serializers.CharField()
    smart_keywords = serializers.ListField(child=serializers.CharField())
    users = UserSearchSerializer(many=True)
    hashtags = HashtagSearchSerializer(many=True)
    posts = serializers.ListField(child=serializers.DictField(), required=False, default=[])


class SearchSuggestionUserSerializer(serializers.Serializer):
    """سریالایزر پیشنهادات کاربر"""
    type = serializers.CharField()
    text = serializers.CharField()
    display = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    id = serializers.UUIDField()


class SearchSuggestionHashtagSerializer(serializers.Serializer):
    type = serializers.CharField()
    text = serializers.CharField()
    count = serializers.IntegerField()
    name = serializers.CharField()


class SearchSuggestionsSerializer(serializers.Serializer):
    users = SearchSuggestionUserSerializer(many=True)
    hashtags = SearchSuggestionHashtagSerializer(many=True)


class SearchConfigSerializer(serializers.Serializer):
    use_ollama = serializers.BooleanField()
    ollama_timeout = serializers.IntegerField()