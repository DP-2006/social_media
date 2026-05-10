# apps/interactions/services/feed_engine.py

from typing import List, Tuple
from django.db.models import Q, F
from .weight_calculator import WeightCalculator
from .statistical_analyzer import StatisticalAnalyzer

class FeedEngine:
    """
    موتور تولید فید هوشمند
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_feed(self, limit: int = 20, offset: int = 0) -> List:
        """
        دریافت پست‌های فید مرتب شده بر اساس وزن
        """
        from apps.posts.models import Post
        from apps.follows.models import Follow
        
        following_ids = Follow.objects.filter(
            follower=self.user,
            is_accepted=True
        ).values_list('following_id', flat=True)
        
        if not following_ids:
            return []
        
        posts = Post.objects.filter(
            user_id__in=following_ids,
            is_private=False
        ).select_related('user__profile').prefetch_related('media')
        
        scored_posts = []
        for post in posts:
            calculator = WeightCalculator(self.user, post)
            weight = calculator.calculate()
            scored_posts.append((weight, post))
        
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        
        paginated = scored_posts[offset:offset+limit]
        
        return [post for weight, post in paginated]
    
    def get_explore(self, limit: int = 30, offset: int = 0) -> List:
        """
        دریافت پست‌های اکسپلور (غیر از فالو شده‌ها)
        با تنوع بالا
        """
        from apps.posts.models import Post
        from apps.follows.models import Follow
        from datetime import datetime, timedelta
        
        following_ids = Follow.objects.filter(
            follower=self.user,
            is_accepted=True
        ).values_list('following_id', flat=True)
        
        week_ago = datetime.now() - timedelta(days=7)
        
        posts = Post.objects.filter(
            created_at__gte=week_ago,
            is_private=False
        ).exclude(
            user_id__in=following_ids
        ).exclude(
            user=self.user
        ).select_related('user__profile')
        
        scored_posts = []
        seen_users = set()
        
        for post in posts:
            if post.user_id in seen_users:
                continue
            
            calculator = WeightCalculator(self.user, post)
            weight = calculator.calculate()
            
            exploration_bonus = 0.1 * (1 - calculator.user_profile.get('consistency_score', 0.5))
            final_weight = weight + exploration_bonus
            
            scored_posts.append((final_weight, post))
            seen_users.add(post.user_id)
        
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        paginated = scored_posts[offset:offset+limit]
        
        return [post for weight, post in paginated]