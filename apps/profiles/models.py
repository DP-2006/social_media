
from django.db import models
from django.conf import settings
import uuid

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    display_name = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')
    #avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profiles/',
        default='defaults/default_avatar.png',
        blank=True
    )
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"پروفایل {self.user.username}"
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()