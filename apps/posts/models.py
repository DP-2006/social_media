
import uuid

from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.models.base_model import BaseModel


class Post(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField()
    
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    file = models.FileField(
        upload_to='posts/files/', 
        blank=True, 
        null=True,
    )
    file_name = models.CharField(max_length=255, blank=True, null=True)  
    file_size = models.BigIntegerField(blank=True, null=True)
    
    is_deleted = models.BooleanField(default=False)  
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Post {self.id} by {self.user}"

    @property
    def likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def like(self, user):
        if not user.is_authenticated:
            return None, False
        
        like, created = Like.objects.get_or_create(user=user, post=self)
        return like, created

    def unlike(self, user):
        if not user.is_authenticated:
            return False
        
        deleted, _ = self.likes.filter(user=user).delete()
        return deleted > 0

    def toggle_like(self, user):
        if not user.is_authenticated:
            return None, False
        
        like, created = Like.objects.get_or_create(   user=user, post=self)
        
        if not created:
            like.delete()
            return False, False
        
        return True, True

    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def all_media(self):
        return self.media_files.all()
    
    @property
    def extra_images(self):
        return self.media_files.filter(file_type='image')
    
    @property
    def extra_files(self):
        return self.media_files.filter(file_type='file')


class PostMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    file = models.FileField(upload_to='posts/media/%Y/%m/%d/')
    file_type = models.CharField(
        max_length=10, 
        db_index=True
    )
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['post', 'file_type']),
            models.Index(fields=['post', 'order']),
        ]

    def __str__(self):
        return f"{self.get_file_type_display()} for post {self.post.id}"

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name.split('/')[-1]
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Like(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'post']]
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} liked post {self.post.id}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)  

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    text = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def is_reply(self):
        return self.parent is not None

    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError("")

    def __str__(self):
        return f"کامنت {self.user.username} روی پست {self.post.id}"


class SavedPost(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,    
        related_name='saved_by_users'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'post']]  
        ordering = ['-saved_at']
        indexes = [
            models.Index(fields=['user', '-saved_at']),
            models.Index(fields=['post', '-saved_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} saved post {self.post.id}"