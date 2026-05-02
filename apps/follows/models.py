# apps/follows/models.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models.base_model import BaseModel


class FollowManager(models.Manager):
    
    def are_following(self, follower, following):
        if follower == following:
            return False
        return self.filter(follower=follower, following=following).exists()
    
    def get_followers(self, user):
        return self.filter(following=user).select_related('follower')
    
    def get_following(self, user):
        return self.filter(follower=user).select_related('following')
    
    def get_followers_count(self, user):
        return self.filter(following=user).count()
    
    def get_following_count(self, user):
        return self.filter(follower=user).count()


class Follow(BaseModel):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_relations'  # changed from 'following' to avoid confusion
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_relations'   # changed from 'followers' to avoid confusion
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FollowManager()

    class Meta:
        unique_together = [['follower', 'following']]
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
            models.Index(fields=['follower', 'following']),  
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(follower=models.F('following')), 
                name='cannot_follow_self'
            )
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("یک کاربر نمی‌تواند خودش را فالو کند.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"