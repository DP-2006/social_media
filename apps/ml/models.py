# apps/ml/models.py

from django.db import models
from django.conf import settings
from core.models.base_model import BaseModel

class MLModelRegistry(BaseModel):
    MODEL_TYPES = [
        ('recommendation', 'موتور پیشنهاد'),
        ('moderation', 'تعدیل محتوا'),
        ('sentiment', 'تحلیل احساسات'),
        ('trending', 'پیش‌بینی ترند'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('training', 'در حال آموزش'),
        ('active', 'فعال'),
        ('failed', 'خطا'),
        ('deprecated', 'منسوخ'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    model_path = models.CharField(max_length=500, blank=True)
    
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    trained_samples = models.IntegerField(default=0)
    training_duration = models.FloatField(null=True, blank=True)
    trained_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict)
    error_log = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-trained_at']
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['-trained_at']),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class TrainingData(BaseModel):
    DATA_TYPES = [
        ('moderation', 'داده تعدیل محتوا'),
        ('interaction', 'داده تعامل کاربر'),
        ('sentiment', 'داده احساسات'),
        ('custom', 'داده سفارشی'),
    ]
    
    data_type = models.CharField(max_length=50, choices=DATA_TYPES)
    source_table = models.CharField(max_length=100)
    features = models.JSONField()
    labels = models.JSONField(null=True, blank=True)
    
    row_count = models.IntegerField()
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    is_validated = models.BooleanField(default=False)
    quality_score = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.data_type} - {self.row_count} samples"


class PredictionCache(BaseModel):
    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    model_type = models.CharField(max_length=50)
    input_hash = models.CharField(max_length=64)
    prediction_result = models.JSONField()
    confidence = models.FloatField()
    
    expires_at = models.DateTimeField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    hit_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['model_type', '-hit_count']),
            models.Index(fields=['expires_at']), 
        ]
    
    def __str__(self):
        return f"{self.model_type}: {self.cache_key}"


class UserEmbedding(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ml_embedding'
    )
    embedding_vector = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
    
    interests = models.JSONField(default=list)
    activity_score = models.FloatField(default=0.0)
    
    class Meta:
        indexes = [
            models.Index(fields=['-activity_score']),
        ]
    
    def __str__(self):
        return f"Embedding for user {self.user.id}"