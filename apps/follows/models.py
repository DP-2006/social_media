from django.db import models

# Create your models here.
# apps/follows/models.py

from django.db import models
from django.conf import settings
from core.models.base_model import BaseModel


class Follow(BaseModel):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'  
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers' 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['follower', 'following']]
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]


        constraints = [
            models.CheckConstraint(
                condition=~models.Q(follower=models.F('following')), 
                name='cannot_follow_self'
            )
        ]




    def __str__(self):
        return f"{self.follower} follows {self.following}"










