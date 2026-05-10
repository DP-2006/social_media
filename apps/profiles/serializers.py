# # apps/profiles/serializers.py
# from rest_framework import serializers
# from .models import Profile
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class ProfileSerializer(serializers.ModelSerializer):
#     """Serializer for Profile model"""
#     user_id = serializers.UUIDField(source='user.id', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     phone = serializers.CharField(source='user.phone', read_only=True)
#     email = serializers.EmailField(source='user.email', read_only=True)
#     followers_count = serializers.SerializerMethodField()
#     following_count = serializers.SerializerMethodField()
#     posts_count = serializers.SerializerMethodField()
#     avatar_url = serializers.SerializerMethodField()
#     is_following = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Profile
#         fields = [
#             'id',
#             'user_id',
#             'username',
#             'phone',
#             'email',
#             'display_name',
#             'bio',
#             'avatar',
#             'avatar_url',
#             'profile_image',
#             'is_private',
#             'is_active',
#             'followers_count',
#             'following_count',
#             'posts_count',
#             'is_following',
#             'created_at',
#             'updated_at',
#         ]
#         read_only_fields = ['id', 'user_id', 'username', 'phone', 'created_at', 'updated_at']
    
#     def get_avatar_url(self, obj):
#         if obj.avatar and hasattr(obj.avatar, 'url'):
#             return obj.avatar.url
#         if obj.profile_image and hasattr(obj.profile_image, 'url'):
#             return obj.profile_image.url
#         return None
    
#     def get_followers_count(self, obj):
#         return obj.followers.count()
    
#     def get_following_count(self, obj):
#         return obj.following.count()
    
#     def get_posts_count(self, obj):
#         try:
#             from apps.posts.models import Post
#             return Post.objects.filter(user=obj.user, is_deleted=False).count()
#         except:
#             return 0
    
#     def get_is_following(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated and request.user != obj.user:
#             return obj.followers.filter(id=request.user.id).exists()
#         return False


# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating Profile"""
#     class Meta:
#         model = Profile
#         fields = [
#             'display_name',
#             'bio',
#             'avatar',
#             'profile_image',
#             'is_private',
#         ]
    
#     def validate_bio(self, value):
#         if value and len(value) > 500:
#             raise serializers.ValidationError("بیوگرافی نمی‌تواند بیشتر از 500 کاراکتر باشد")
#         return value
    
#     def validate_display_name(self, value):
#         if value and len(value) > 100:
#             raise serializers.ValidationError("نام نمایشی نمی‌تواند بیشتر از 100 کاراکتر باشد")
#         return value


# class UserProfileSerializer(serializers.ModelSerializer):
#     """Serializer for User with profile"""
#     profile = ProfileSerializer(read_only=True)
#     full_name = serializers.CharField(source='profile.display_name', read_only=True)
    
#     class Meta:
#         model = User
#         fields = [
#             'id', 'phone', 'username', 'email', 
#             'profile', 'full_name', 'date_joined', 'last_login'
#         ]
#         read_only_fields = ['id', 'date_joined', 'last_login']


# # ========== Request/Response Serializers ==========
# class SearchUserQuerySerializer(serializers.Serializer):
#     """Serializer for search user query parameters"""
#     q = serializers.CharField(
#         required=True,
#         min_length=1,
#         max_length=100,
#         help_text="Search query for username or display name"
#     )
#     limit = serializers.IntegerField(
#         required=False,
#         default=20,
#         min_value=1,
#         max_value=50,
#         help_text="Maximum number of results to return"
#     )


# class UserIdSerializer(serializers.Serializer):
#     """Serializer for user ID validation"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user"
#     )


# class FollowToggleResponseSerializer(serializers.Serializer):
#     """Serializer for follow toggle response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.ChoiceField(choices=['followed', 'unfollowed'])
#     message = serializers.CharField()


# class FollowUserResponseSerializer(serializers.Serializer):
#     """Serializer for follow user response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.CharField()
#     message = serializers.CharField()


# class ProfileResponseSerializer(serializers.Serializer):
#     """Serializer for profile response"""
#     success = serializers.BooleanField(default=True)
#     data = ProfileSerializer()


# class ProfileUpdateResponseSerializer(serializers.Serializer):
#     """Serializer for profile update response"""
#     success = serializers.BooleanField(default=True)
#     message = serializers.CharField()
#     data = ProfileSerializer()


# class FollowListUserSerializer(serializers.Serializer):
#     """Serializer for individual user in follow list"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     avatar = serializers.URLField(allow_null=True)
#     phone = serializers.CharField(required=False, allow_null=True)


# class FollowListResponseSerializer(serializers.Serializer):
#     """Serializer for followers/following list response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = FollowListUserSerializer(many=True)


# class SearchUserResultSerializer(serializers.Serializer):
#     """Serializer for individual search result"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     avatar = serializers.URLField(allow_null=True)
#     is_private = serializers.BooleanField()
#     is_following = serializers.BooleanField(default=False)


# class SearchUserResponseSerializer(serializers.Serializer):
#     """Serializer for search user response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = SearchUserResultSerializer(many=True)


# class ErrorResponseSerializer(serializers.Serializer):
#     """Serializer for error response"""
#     success = serializers.BooleanField(default=False)
#     error = serializers.CharField()
#     errors = serializers.DictField(required=False)





# apps/profiles/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Profile

# User = get_user_model()


# class ProfileSerializer(serializers.ModelSerializer):
#     """Serializer for Profile model"""
#     user_id = serializers.UUIDField(source='user.id', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     phone = serializers.CharField(source='user.phone', read_only=True)
#     email = serializers.EmailField(source='user.email', read_only=True)
#     followers_count = serializers.SerializerMethodField()
#     following_count = serializers.SerializerMethodField()
#     posts_count = serializers.SerializerMethodField()
#     profile_image_url = serializers.SerializerMethodField()
#     is_following = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Profile
#         fields = [
#             'id', 'user_id', 'username', 'phone', 'email',
#             'display_name', 'bio', 'profile_image', 'profile_image_url',
#             'is_private', 'is_active', 'followers_count', 'following_count', 
#             'posts_count', 'is_following', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'user_id', 'username', 'phone', 'created_at', 'updated_at']
    
#     def get_profile_image_url(self, obj):
#         if obj.profile_image and hasattr(obj.profile_image, 'url'):
#             return obj.profile_image.url
#         return None
    
#     def get_followers_count(self, obj):
#         return obj.followers.count()
    
#     def get_following_count(self, obj):
#         return obj.following.count()
    
#     def get_posts_count(self, obj):
#         try:
#             from apps.posts.models import Post
#             return Post.objects.filter(user=obj.user, is_deleted=False).count()
#         except:
#             return 0
    
#     def get_is_following(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated and request.user != obj.user:
#             return obj.followers.filter(id=request.user.id).exists()
#         return False


# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating Profile"""
#     class Meta:
#         model = Profile
#         fields = ['display_name', 'bio', 'profile_image', 'is_private']
    
#     def validate_bio(self, value):
#         if value and len(value) > 500:
#             raise serializers.ValidationError("بیوگرافی نمی‌تواند بیشتر از 500 کاراکتر باشد")
#         return value
    
#     def validate_display_name(self, value):
#         if value and len(value) > 100:
#             raise serializers.ValidationError("نام نمایشی نمی‌تواند بیشتر از 100 کاراکتر باشد")
#         return value


# class UserProfileSerializer(serializers.ModelSerializer):
#     """Serializer for User with profile"""
#     profile = ProfileSerializer(read_only=True)
#     full_name = serializers.CharField(source='profile.display_name', read_only=True)
    
#     class Meta:
#         model = User
#         fields = [
#             'id', 'phone', 'username', 'email', 
#             'profile', 'full_name', 'date_joined', 'last_login'
#         ]
#         read_only_fields = ['id', 'date_joined', 'last_login']


# # ========== Request/Response Serializers ==========
# class ProfileUserIdSerializer(serializers.Serializer):
#     """Serializer for user ID validation"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user"
#     )


# class ProfileSearchQuerySerializer(serializers.Serializer):
#     """Serializer for search user query parameters"""
#     q = serializers.CharField(
#         required=True,
#         min_length=1,
#         max_length=100,
#         help_text="Search query for username or display name"
#     )
#     limit = serializers.IntegerField(
#         required=False,
#         default=20,
#         min_value=1,
#         max_value=50,
#         help_text="Maximum number of results to return"
#     )


# class ProfileFollowToggleResponseSerializer(serializers.Serializer):
#     """Serializer for follow toggle response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.CharField()
#     message = serializers.CharField()


# class ProfileResponseSerializer(serializers.Serializer):
#     """Serializer for profile response"""
#     success = serializers.BooleanField(default=True)
#     data = ProfileSerializer()


# class ProfileUpdateResponseSerializer(serializers.Serializer):
#     """Serializer for profile update response"""
#     success = serializers.BooleanField(default=True)
#     message = serializers.CharField()
#     data = ProfileSerializer()


# class ProfileFollowListUserSerializer(serializers.Serializer):
#     """Serializer for individual user in follow list"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     profile_image = serializers.URLField(allow_null=True)
#     phone = serializers.CharField(required=False, allow_null=True)


# class ProfileFollowListResponseSerializer(serializers.Serializer):
#     """Serializer for followers/following list response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = ProfileFollowListUserSerializer(many=True)


# class ProfileSearchResultSerializer(serializers.Serializer):
#     """Serializer for individual search result"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     profile_image = serializers.URLField(allow_null=True)
#     is_private = serializers.BooleanField()
#     is_following = serializers.BooleanField(default=False)


# class ProfileSearchResponseSerializer(serializers.Serializer):
#     """Serializer for search user response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = ProfileSearchResultSerializer(many=True)












# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Profile

# User = get_user_model()


# class ProfileSerializer(serializers.ModelSerializer):
#     """Serializer for Profile model"""
#     user_id = serializers.UUIDField(source='user.id', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     phone = serializers.CharField(source='user.phone', read_only=True)
#     email = serializers.EmailField(source='user.email', read_only=True)
#     followers_count = serializers.SerializerMethodField()
#     following_count = serializers.SerializerMethodField()
#     posts_count = serializers.SerializerMethodField()
#     profile_image_url = serializers.SerializerMethodField()
#     is_following = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Profile
#         fields = [
#             'id', 'user_id', 'username', 'phone', 'email',
#             'display_name', 'bio', 'profile_image', 'profile_image_url',
#             'is_private', 'is_active', 'followers_count', 'following_count', 
#             'posts_count', 'is_following', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'user_id', 'username', 'phone', 'created_at', 'updated_at']
    
#     def get_profile_image_url(self, obj) -> str | None:
#         if obj.profile_image and hasattr(obj.profile_image, 'url'):
#             return obj.profile_image.url
#         return None
    
#     def get_followers_count(self, obj) -> int:
#         return obj.followers.count()
    
#     def get_following_count(self, obj) -> int:
#         return obj.following.count()
    
#     def get_posts_count(self, obj) -> int:
#         try:
#             from apps.posts.models import Post
#             return Post.objects.filter(user=obj.user, is_deleted=False).count()
#         except:
#             return 0
    
#     def get_is_following(self, obj) -> bool:
#         request = self.context.get('request')
#         if request and request.user.is_authenticated and request.user != obj.user:
#             return obj.followers.filter(id=request.user.id).exists()
#         return False


# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating Profile"""
#     class Meta:
#         model = Profile
#         fields = ['display_name', 'bio', 'profile_image', 'is_private']
    
#     def validate_bio(self, value) -> str:
#         if value and len(value) > 500:
#             raise serializers.ValidationError("بیوگرافی نمی‌تواند بیشتر از 500 کاراکتر باشد")
#         return value
    
#     def validate_display_name(self, value) -> str:
#         if value and len(value) > 100:
#             raise serializers.ValidationError("نام نمایشی نمی‌تواند بیشتر از 100 کاراکتر باشد")
#         return value


# class UserProfileSerializer(serializers.ModelSerializer):
#     """Serializer for User with profile"""
#     profile = ProfileSerializer(read_only=True)
#     full_name = serializers.CharField(source='profile.display_name', read_only=True)
    
#     class Meta:
#         model = User
#         fields = [
#             'id', 'phone', 'username', 'email', 
#             'profile', 'full_name', 'date_joined', 'last_login'
#         ]
#         read_only_fields = ['id', 'date_joined', 'last_login']


# # ========== Request/Response Serializers ==========
# class ProfileUserIdSerializer(serializers.Serializer):
#     """Serializer for user ID validation"""
#     user_id = serializers.IntegerField(
#         required=True,
#         help_text="ID of the user"
#     )


# class ProfileSearchQuerySerializer(serializers.Serializer):
#     """Serializer for search user query parameters"""
#     q = serializers.CharField(
#         required=True,
#         min_length=1,
#         max_length=100,
#         help_text="Search query for username or display name"
#     )
#     limit = serializers.IntegerField(
#         required=False,
#         default=20,
#         min_value=1,
#         max_value=50,
#         help_text="Maximum number of results to return"
#     )


# class ProfileFollowToggleResponseSerializer(serializers.Serializer):
#     """Serializer for follow toggle response"""
#     success = serializers.BooleanField(default=True)
#     action = serializers.CharField()
#     message = serializers.CharField()


# class ProfileResponseSerializer(serializers.Serializer):
#     """Serializer for profile response"""
#     success = serializers.BooleanField(default=True)
#     data = ProfileSerializer()


# class ProfileUpdateResponseSerializer(serializers.Serializer):
#     """Serializer for profile update response"""
#     success = serializers.BooleanField(default=True)
#     message = serializers.CharField()
#     data = ProfileSerializer()


# class ProfileFollowListUserSerializer(serializers.Serializer):
#     """Serializer for individual user in follow list"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     profile_image = serializers.URLField(allow_null=True)
#     phone = serializers.CharField(required=False, allow_null=True)


# class ProfileFollowListResponseSerializer(serializers.Serializer):
#     """Serializer for followers/following list response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = ProfileFollowListUserSerializer(many=True)


# class ProfileSearchResultSerializer(serializers.Serializer):
#     """Serializer for individual search result"""
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     display_name = serializers.CharField(allow_null=True)
#     profile_image = serializers.URLField(allow_null=True)
#     is_private = serializers.BooleanField()
#     is_following = serializers.BooleanField(default=False)


# class ProfileSearchResponseSerializer(serializers.Serializer):
#     """Serializer for search user response"""
#     success = serializers.BooleanField(default=True)
#     count = serializers.IntegerField()
#     data = ProfileSearchResultSerializer(many=True)


# class ErrorResponseSerializer(serializers.Serializer):
#     """Serializer for error response"""
#     success = serializers.BooleanField(default=False)
#     error = serializers.CharField()
#     errors = serializers.DictField(required=False)















from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user_id', 'username', 'phone', 'email',
            'display_name', 'bio', 'profile_image', 'profile_image_url',
            'is_private', 'is_active', 'followers_count', 'following_count', 
            'posts_count', 'is_following', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'username', 'phone', 'created_at', 'updated_at']
    
    def get_profile_image_url(self, obj) -> str | None:
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return obj.profile_image.url
        return None
    
    def get_followers_count(self, obj) -> int:
        from apps.follows.models import Follow
        #return Follow.objects.filter(following=obj.user).count()
        return obj.followers.count() if hasattr(obj, 'followers') else 0
    
    def get_following_count(self, obj) -> int:
        from apps.follows.models import Follow
        return Follow.objects.filter(follower=obj.user).count()
    
    def get_posts_count(self, obj) -> int:
        try:
            from apps.posts.models import Post
            return Post.objects.filter(user=obj.user, is_deleted=False).count()
        except:
            return 0
    
    def get_is_following(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            from apps.follows.models import Follow
            return Follow.objects.filter(follower=request.user, following=obj.user).exists()
        return False


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Profile"""
    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'profile_image', 'is_private']
    
    def validate_bio(self, value) -> str:
        if value and len(value) > 500:
            raise serializers.ValidationError("بیوگرافی نمی‌تواند بیشتر از 500 کاراکتر باشد")
        return value
    
    def validate_display_name(self, value) -> str:
        if value and len(value) > 100:
            raise serializers.ValidationError("نام نمایشی نمی‌تواند بیشتر از 100 کاراکتر باشد")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User with profile"""
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='profile.display_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'username', 'email', 
            'profile', 'full_name', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


# ========== Request/Response Serializers ==========
class ProfileUserIdSerializer(serializers.Serializer):
    """Serializer for user ID validation"""
    user_id = serializers.IntegerField(
        required=True,
        help_text="ID of the user"
    )


class ProfileSearchQuerySerializer(serializers.Serializer):
    """Serializer for search user query parameters"""
    q = serializers.CharField(
        required=True,
        min_length=1,
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


class ProfileFollowToggleResponseSerializer(serializers.Serializer):
    """Serializer for follow toggle response"""
    success = serializers.BooleanField(default=True)
    action = serializers.CharField()
    message = serializers.CharField()


class ProfileResponseSerializer(serializers.Serializer):
    """Serializer for profile response"""
    success = serializers.BooleanField(default=True)
    data = ProfileSerializer()


class ProfileUpdateResponseSerializer(serializers.Serializer):
    """Serializer for profile update response"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = ProfileSerializer()


class ProfileFollowListUserSerializer(serializers.Serializer):
    """Serializer for individual user in follow list"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField(allow_null=True)
    profile_image = serializers.URLField(allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)


class ProfileFollowListResponseSerializer(serializers.Serializer):
    """Serializer for followers/following list response"""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = ProfileFollowListUserSerializer(many=True)


class ProfileSearchResultSerializer(serializers.Serializer):
    """Serializer for individual search result"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField(allow_null=True)
    profile_image = serializers.URLField(allow_null=True)
    is_private = serializers.BooleanField()
    is_following = serializers.BooleanField(default=False)


class ProfileSearchResponseSerializer(serializers.Serializer):
    """Serializer for search user response"""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = ProfileSearchResultSerializer(many=True)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error response"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    errors = serializers.DictField(required=False)