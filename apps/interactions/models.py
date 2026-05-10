from django.db import models

from django.db import models
from django.conf import settings
from core.models.base_model import BaseModel
class UserPostEngagement(models.Model):
    """
    مدل علمی برای ثبت تعامل کاربر با پست
    """
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    
    view_duration_ms = models.IntegerField(
        null=True, blank=True,
        help_text="مدت زمان نگاه کردن به پست به میلی‌ثانیه"
    )
    scroll_depth = models.IntegerField(default=0, help_text="درصد اسکرول شده")
    visibility_ratio = models.FloatField(default=1.0)
    
    liked_at = models.DateTimeField(null=True, blank=True)
    saved_at = models.DateTimeField(null=True, blank=True)
    shared_at = models.DateTimeField(null=True, blank=True)
    
    attention_index = models.FloatField(default=0.0)
    engagement_depth = models.FloatField(default=0.0)
    total_value_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['user', '-total_value_score']),
            models.Index(fields=['post', '-total_value_score']),
        ]







class UserInteraction(BaseModel):
    """مدل موجود شما - نگه دار"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_interactions')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions_with_me')
    interaction_type = models.CharField(max_length=20)
    interaction_weight = models.FloatField(default=1.0)
    
    class Meta:
        unique_together = ['user', 'target_user', 'interaction_type']


class UserPostEngagement(models.Model):
    """
    ثبت دقیق تعامل کاربر با هر پست
    این مدل قلب سیستم فید هوشمند است
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='post_engagements'
    )
    post = models.ForeignKey(
        'posts.Post', 
        on_delete=models.CASCADE, 
        related_name='user_engagements'
    )
    
    view_duration_ms = models.IntegerField(
        null=True, 
        blank=True,
        help_text="مدت زمان نگاه کردن به پست به میلی‌ثانیه"
    )
    scroll_depth = models.IntegerField(
        default=0, 
        help_text="درصد اسکرول شده (0-100)"
    )
    visibility_ratio = models.FloatField(
        default=1.0,
        help_text="نسبت زمانی که پست در viewport بوده"
    )
    
    liked_at = models.DateTimeField(null=True, blank=True)
    saved_at = models.DateTimeField(null=True, blank=True)
    shared_at = models.DateTimeField(null=True, blank=True)
    commented_at = models.DateTimeField(null=True, blank=True)
    
    attention_index = models.FloatField(
        default=0.0,
        help_text="نمره توجه بر اساس Z-Score"
    )
    engagement_depth = models.FloatField(
        default=0.0,
        help_text="عمق تعامل (لایک، ذخیره، اشتراک)"
    )
    total_value_score = models.FloatField(
        default=0.0,
        help_text="وزن نهایی پست برای این کاربر"
    )
    
    is_outlier = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['user', '-total_value_score']),
            models.Index(fields=['post', '-total_value_score']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.post.id[:8]} - {self.total_value_score:.2f}"