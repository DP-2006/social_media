# apps/interactions/services/statistical_analyzer.py

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from django.db.models import Avg, StdDev, Count, Q

@dataclass
class StatisticalMetrics:
    """متریک‌های آماری کامل"""
    mean: float = 0.0
    median: float = 0.0
    variance: float = 0.0
    std_dev: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    confidence_interval_low: float = 0.0
    confidence_interval_high: float = 0.0
    outlier_ratio: float = 0.0
    sample_size: int = 0
    is_reliable: bool = False
    
class StatisticalAnalyzer:
    """تحلیلگر آماری برای داده‌های تعامل"""
    
    @staticmethod
    def analyze_post_engagement(post_id: str) -> StatisticalMetrics:
        """
        تحلیل آماری کامل تعاملات یک پست
        """
        from apps.interactions.models import UserPostEngagement
        

        engagements = UserPostEngagement.objects.filter(
            post_id=post_id,
            view_duration_ms__isnull=False,
            view_duration_ms__gt=0,  
            
            is_outlier=False  
            
        ).values_list('view_duration_ms', flat=True)
        
        durations = list(engagements)
        metrics = StatisticalMetrics(sample_size=len(durations))
        
        if len(durations) < 3:
            metrics.is_reliable = False
            return metrics
        

        durations_array = np.array(durations)
        metrics.mean = float(np.mean(durations_array))
        metrics.median = float(np.median(durations_array))
        metrics.variance = float(np.var(durations_array))
        metrics.std_dev = float(np.std(durations_array))
        metrics.min_val = float(np.min(durations_array))
        metrics.max_val = float(np.max(durations_array))
        

        if len(durations) > 2:
            from scipy import stats
            metrics.skewness = float(stats.skew(durations_array))
            metrics.kurtosis = float(stats.kurtosis(durations_array))
        

        if len(durations) > 1:
            from scipy import stats
            sem = stats.sem(durations_array)
            confidence = stats.t.interval(0.95, len(durations)-1, metrics.mean, sem)
            metrics.confidence_interval_low = float(confidence[0])
            metrics.confidence_interval_high = float(confidence[1])

        q1, q3 = np.percentile(durations_array, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [d for d in durations if d < lower_bound or d > upper_bound]
        metrics.outlier_ratio = len(outliers) / len(durations) if durations else 0
        
        metrics.is_reliable = (
            metrics.sample_size >= 10 and
            metrics.outlier_ratio <= 0.1 and
            metrics.variance > 100 and  
            metrics.variance < 1000000  
        )
        
        return metrics
    
    @staticmethod
    def get_user_behavior_profile(user_id: str) -> Dict:
        """
        پروفایل رفتاری کاربر بر اساس واریانس و ثبات
        """
        from apps.interactions.models import UserPostEngagement
        
        view_times = UserPostEngagement.objects.filter(
            user_id=user_id,
            view_duration_ms__isnull=False,
            view_duration_ms__gt=0
        ).values_list('view_duration_ms', flat=True)
        
        times = list(view_times)
        
        if len(times) < 5:
            return {
                'variance': 0,
                'std_dev': 0,
                'coefficient_of_variation': 0,
                'consistency_score': 0.5,
                'avg_view_time': 0,
                'sample_size': len(times),
                'behavior_type': 'unknown'
            }
        
        times_array = np.array(times)
        variance = float(np.var(times_array))
        std_dev = float(np.std(times_array))
        mean_time = float(np.mean(times_array))
        
        cv = std_dev / mean_time if mean_time > 0 else 0
        
        consistency_score = float(1 / (1 + cv)) if cv > 0 else 1.0
        
        if consistency_score > 0.7:
            behavior_type = 'stable'  
        elif consistency_score < 0.3:
            behavior_type = 'volatile' 
        else:
            behavior_type = 'normal'
        
        return {
            'variance': variance,
            'std_dev': std_dev,
            'coefficient_of_variation': cv,
            'consistency_score': consistency_score,
            'avg_view_time': mean_time,
            'sample_size': len(times),
            'behavior_type': behavior_type
        }