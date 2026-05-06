# apps/ml/serializers.py

from rest_framework import serializers
from .models import MLModelRegistry, TrainingData, PredictionCache, UserEmbedding

class MLModelRegistrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MLModelRegistry
        fields = [
            'id', 'model_type', 'version', 'file_path',
            'status', 'accuracy', 'precision', 'recall', 'f1_score',
            'trained_at', 'training_duration', 'training_data_size',
            'metadata', 'is_active'
        ]
        read_only_fields = ['id', 'trained_at', 'file_path']


class TrainingDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TrainingData
        fields = [
            'id', 'data_type', 'features', 'labels',
            'collected_at', 'is_used_in_training'
        ]
        read_only_fields = ['id', 'collected_at']


class PredictionCacheSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PredictionCache
        fields = [
            'id', 'cache_key', 'model_type', 'input_hash',
            'prediction_result', 'confidence_score', 'created_at',
            'last_accessed', 'access_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_accessed', 'access_count']


class UserEmbeddingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserEmbedding
        fields = [
            'id', 'user', 'embedding_vector', 'dimension',
            'created_at', 'updated_at', 'version'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']



class ContentModerationRequestSerializer(serializers.Serializer):
    """سریالایزر درخواست تعدیل محتوا"""
    content = serializers.CharField(
        required=True,
        max_length=5000,
        help_text="متن مورد نظر برای بررسی"
    )
    type = serializers.ChoiceField(
        choices=['post', 'comment', 'bio', 'message'],
        default='comment',
        help_text="نوع محتوا"
    )
    language = serializers.CharField(
        required=False,
        default='fa',
        help_text="زبان محتوا (fa/en)"
    )


class ContentModerationResponseSerializer(serializers.Serializer):
    """سریالایزر پاسخ تعدیل محتوا"""
    is_appropriate = serializers.BooleanField(
        help_text="آیا محتوا مناسب است؟"
    )
    confidence = serializers.FloatField(
        help_text="میزان اطمینان مدل (0 تا 1)"
    )
    categories = serializers.DictField(
        required=False,
        help_text="دسته‌بندی‌های تشخیص داده شده"
    )
    violations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="لیست موارد تخلف"
    )
    requires_review = serializers.BooleanField(
        default=False,
        help_text="آیا نیاز به بررسی دستی دارد؟"
    )
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="پیشنهادات برای اصلاح"
    )


class PersonalizedFeedResponseSerializer(serializers.Serializer):
    posts = serializers.ListField(
        help_text="لیست پست‌های پیشنهادی"
    )
    recommendation_metadata = serializers.DictField(
        help_text="متادیتای پیشنهادات"
    )


class TrainModelRequestSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(
        choices=['recommendation', 'moderation', 'sentiment', 'trending', 'all'],
        default='all',
        help_text="نوع مدل برای آموزش"
    )
    force_retrain = serializers.BooleanField(
        default=False,
        help_text="اجبار به آموزش مجدد حتی اگر مدل جدید نباشد"
    )
    use_gpu = serializers.BooleanField(
        default=False,
        help_text="استفاده از GPU برای آموزش"
    )
    validation_split = serializers.FloatField(
        default=0.2,
        min_value=0.1,
        max_value=0.4,
        help_text="نسبت داده‌های اعتبارسنجی"
    )


class TrainModelResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    result = serializers.DictField()


class ModelStatusSerializer(serializers.Serializer):
    type = serializers.CharField(help_text="نوع مدل")
    version = serializers.CharField(help_text="نسخه مدل")
    status = serializers.CharField(help_text="وضعیت مدل")
    accuracy = serializers.FloatField(allow_null=True, help_text="دقت مدل")
    trained_at = serializers.DateTimeField(help_text="زمان آخرین آموزش")
    is_active = serializers.BooleanField(help_text="آیا مدل فعال است؟")


class ModelHealthResponseSerializer(serializers.Serializer):
    models = ModelStatusSerializer(many=True)
    total_models = serializers.IntegerField()


class ModelPredictionRequestSerializer(serializers.Serializer):
    
    model_type = serializers.ChoiceField(
        choices=['recommendation', 'moderation', 'sentiment', 'trending'],
        required=True,
        help_text="نوع مدل مورد نظر"
    )
    input_data = serializers.DictField(
        required=True,
        help_text="داده‌های ورودی برای پیش‌بینی"
    )
    use_cache = serializers.BooleanField(
        default=True,
        help_text="آیا از کش استفاده شود؟"
    )


class ModelPredictionResponseSerializer(serializers.Serializer):
    prediction = serializers.JSONField(help_text="نتیجه پیش‌بینی")
    confidence = serializers.FloatField(help_text="میزان اطمینان")
    model_version = serializers.CharField(help_text="نسخه مدل استفاده شده")
    processing_time_ms = serializers.FloatField(help_text="زمان پردازش به میلی‌ثانیه")
    from_cache = serializers.BooleanField(help_text="آیا از کش برگشته است؟")



class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)


class ValidationErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    field_errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False
    )

class EvaluationMetricsSerializer(serializers.Serializer):
    accuracy = serializers.FloatField(required=False)
    precision = serializers.FloatField(required=False)
    recall = serializers.FloatField(required=False)
    f1_score = serializers.FloatField(required=False)
    roc_auc = serializers.FloatField(required=False)
    log_loss = serializers.FloatField(required=False)
    confusion_matrix = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField()),
        required=False
    )


class TrainingHistorySerializer(serializers.Serializer):
    epoch = serializers.IntegerField()
    train_loss = serializers.FloatField()
    val_loss = serializers.FloatField()
    train_accuracy = serializers.FloatField(required=False)
    val_accuracy = serializers.FloatField(required=False)
    learning_rate = serializers.FloatField(required=False)
    timestamp = serializers.DateTimeField()


class BatchPredictionRequestSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(
        choices=['recommendation', 'moderation', 'sentiment', 'trending'],
        required=True
    )
    inputs = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100,
        help_text="لیست داده‌های ورودی (حداکثر ۱۰۰ آیتم)"
    )
    use_cache = serializers.BooleanField(default=True)


class BatchPredictionResponseSerializer(serializers.Serializer):
    results = serializers.ListField(
        child=ModelPredictionResponseSerializer()
    )
    total_processed = serializers.IntegerField()
    total_time_ms = serializers.FloatField()
    cache_hit_count = serializers.IntegerField()


















# apps/ml/serializers.py (اضافه کردن این سریالایزرها)

from rest_framework import serializers

class PhoneNumberSerializer(serializers.Serializer):
    """سریالایزر برای شماره موبایل"""
    phone_number = serializers.CharField(
        required=True,
        max_length=15,
        help_text="شماره موبایل کاربر"
    )

class BulkAnalysisSerializer(serializers.Serializer):
    """سریالایزر برای تحلیل دسته‌ای"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="لیست شناسه‌های کاربران"
    )
    include_details = serializers.BooleanField(
        default=True,
        required=False,
        help_text="آیا جزئیات کامل برگردانده شود؟"
    )

class UserAnalysisSerializer(serializers.Serializer):
    """سریالایزر خروجی تحلیل"""
    success = serializers.BooleanField()
    data = serializers.DictField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

class ComparisonSerializer(serializers.Serializer):
    """سریالایزر مقایسه دو کاربر"""
    similarity_score = serializers.FloatField()
    user1 = serializers.DictField()
    user2 = serializers.DictField()
    comparison_details = serializers.DictField()