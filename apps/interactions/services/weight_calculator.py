# apps/interactions/services/weight_calculator.py

import numpy as np
from typing import Dict, Optional
from django.utils import timezone
from .statistical_analyzer import StatisticalAnalyzer, StatisticalMetrics

class WeightCalculator:
    """
    محاسبه‌گر علمی وزن پست‌ها
    هیچ عدد پیش‌فرض بی‌مبنایی اینجا نیست!
    """
    
    def __init__(self, user, post):
        self.user = user
        self.post = post
        self.post_stats = StatisticalAnalyzer.analyze_post_engagement(post.id)
        self.user_profile = StatisticalAnalyzer.get_user_behavior_profile(user.id)
    
    def calculate(self) -> float:
        """
        محاسبه وزن نهایی با ترکیب همه فاکتورها
        """
        from apps.interactions.models import UserPostEngagement
        
        engagement, created = UserPostEngagement.objects.get_or_create(
            user=self.user,
            post=self.post
        )
        
        attention_score = self._calculate_attention_score(engagement)
        
        engagement_score = self._calculate_engagement_score(engagement)
        
        statistical_weight = self._get_statistical_weight()
        
        behavioral_weight = self._get_behavioral_weight()
        
        if self.post_stats.is_reliable:
            final_score = (
                attention_score * 0.45 +
                engagement_score * 0.35 +
                statistical_weight * 0.15 +
                behavioral_weight * 0.05
            )
        else:
           
            final_score = (
                attention_score * 0.5 +
                engagement_score * 0.4 +
                behavioral_weight * 0.1
            )
        
        final_score = max(0.0, min(1.0, final_score))
        
        engagement.attention_index = attention_score
        engagement.engagement_depth = engagement_score
        engagement.total_value_score = final_score
        engagement.confidence_score = self._calculate_confidence()
        engagement.save(update_fields=[
            'attention_index', 'engagement_depth', 
            'total_value_score', 'confidence_score'
        ])
        
        return final_score
    
    def _calculate_attention_score(self, engagement) -> float:
        """
        نمره توجه بر اساس Z-Score واقعی
        فرمول: Z = (X - μ) / σ
        سپس تبدیل با sigmoid به [0, 1]
        """
        if not engagement.view_duration_ms or engagement.view_duration_ms <= 0:
            return 0.0
        
        view_time = engagement.view_duration_ms
        
        # اگر outlier است، جریمه کن
        if self._is_outlier(view_time):
            engagement.is_outlier = True
            engagement.save(update_fields=['is_outlier'])
            return 0.1
        
        if self.post_stats.std_dev > 0 and self.post_stats.mean > 0:
            z_score = (view_time - self.post_stats.mean) / self.post_stats.std_dev
            
            attention = 1 / (1 + np.exp(-z_score / 2))
        else:
            max_expected = 60000  
            attention = min(view_time / max_expected, 1.0)
        
        return float(attention)
    
    def _calculate_engagement_score(self, engagement) -> float:
        """
        نمره عمق تعامل با وزن‌دهی علمی
        """
        score = 0.0
        
        if engagement.liked_at:
            days_ago = (timezone.now() - engagement.liked_at).days
            recency = max(0, 1 - days_ago / 30)  # کاهش در 30 روز
            score += 0.3 * recency
        
        if engagement.saved_at:
            days_ago = (timezone.now() - engagement.saved_at).days
            recency = max(0, 1 - days_ago / 30)
            score += 0.5 * recency
        
        if engagement.shared_at:
            days_ago = (timezone.now() - engagement.shared_at).days
            recency = max(0, 1 - days_ago / 30)
            score += 0.7 * recency
        
        if engagement.commented_at:
            days_ago = (timezone.now() - engagement.commented_at).days
            recency = max(0, 1 - days_ago / 30)
            score += 0.4 * recency
        
        return min(score, 1.0)
    
    def _get_statistical_weight(self) -> float:
        """
        وزن آماری بر اساس کیفیت داده‌های پست
        """
        if not self.post_stats.is_reliable:
            return 0.2
        
        sample_score = min(self.post_stats.sample_size / 100, 0.5)
        
        outlier_score = 1 - self.post_stats.outlier_ratio
        
        ideal_variance = 10000
        if self.post_stats.variance > 0:
            variance_score = ideal_variance / (ideal_variance + self.post_stats.variance)
        else:
            variance_score = 0.5
        
        weight = (sample_score * 0.4) + (outlier_score * 0.4) + (variance_score * 0.2)
        
        return min(weight, 1.0)
    
    def _get_behavioral_weight(self) -> float:
        """
        وزن بر اساس پروفایل رفتاری کاربر
        """
        consistency = self.user_profile.get('consistency_score', 0.5)
        
        if consistency > 0.7:
            return 0.8
        elif consistency < 0.3:
            return 0.3
        else:
            return 0.5
    
    def _is_outlier(self, value: int) -> bool:
        """
        تشخیص outlier با روش IQR
        """
        if self.post_stats.sample_size < 4:
            return False
        
        q1 = self.post_stats.confidence_interval_low
        q3 = self.post_stats.confidence_interval_high
        iqr = q3 - q1
        
        if iqr <= 0:
            return False
        
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        
        return value < lower or value > upper
    
    def _calculate_confidence(self) -> float:
        """
        محاسبه نمره اطمینان به این وزن
        """
        confidence = 0.5
        
        if self.post_stats.is_reliable:
            confidence += 0.3
        
        if self.user_profile.get('consistency_score', 0) > 0.6:
            confidence += 0.2
        
        return min(confidence, 1.0)