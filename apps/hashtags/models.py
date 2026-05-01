from django.db import models

# Create your models here.
# apps/hashtags/models.py

from django.db import models
from django.conf import settings
from core.models.base_model import BaseModel


class Hashtag(BaseModel):
    name = models.CharField(max_length=100, unique=True)  
    usage_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['-usage_count']),
        ]

    def __str__(self):
        return f"#{self.name}"

    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class PostHashtag(BaseModel):
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='post_hashtags'
    )
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.CASCADE,
        related_name='post_hashtags'
    )

    class Meta:
        unique_together = [['post', 'hashtag']]

    def __str__(self):
        return f"{self.post.id} - #{self.hashtag.name}"