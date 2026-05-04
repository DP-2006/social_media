from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user_id',
            'username',
            'phone',
            'display_name',
            'bio',
            
            'profile_image',
            'is_private',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user_id', 'username', 'phone', 'created_at', 'updated_at']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'bio',
            
            'profile_image',
            'is_private',
        ]
    
    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("bio is not have the over 500 car ")
        return value
    
    def validate_display_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("name cant is bigger the 100 car ")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined']