# apps/ml/services/smart_feed_service.py

import logging
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.core.cache import cache

from apps.posts.models import Post
from apps.hashtags.models import PostHashtag
from apps.follows.models import Follow
from .ollama_hashtag_service import OllamaHashtagService

logger = logging.getLogger(__name__)


class SmartFeedService:
    
    def __init__(self, user):
        self.user = user
        self.ollama_service = OllamaHashtagService(user)
    
    def get_smart_feed(self, limit=20, offset=0, use_ollama=True):
        
        cache_key = f"smart_feed_{self.user.id}_{offset}_{limit}_{use_ollama}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        # دریافت هشتگ‌های پیشنهادی
        if use_ollama:
            recommended_hashtags = self.ollama_service.get_recommended_hashtags()
        else:
            recommended_hashtags = self._get_fallback_hashtags()
        
        # جستجوی پست‌ها
        posts = self._search_posts_by_hashtags(recommended_hashtags, limit * 2)
        
        # تکمیل با پست‌های پرطرفدار اگر کافی نبود
        if len(posts) < limit:
            extra_posts = self._get_trending_posts(limit - len(posts))
            posts = list(posts) + list(extra_posts)
        
        # رتبه‌بندی
        scored_posts = self._rank_posts(posts, recommended_hashtags)
        
        result_posts = scored_posts[offset:offset + limit]
        
        output = {
            'posts': [item['post'] for item in result_posts],
            'scores': [item['score'] for item in result_posts],
            'reasons': [item['reasons'] for item in result_posts],
            'used_hashtags': recommended_hashtags,
            'total_count': len(scored_posts),
            'has_next': offset + limit < len(scored_posts)
        }
        
        cache.set(cache_key, output, 60 * 5)
        
        return output
    
    def _search_posts_by_hashtags(self, hashtags, limit):
        """جستجوی پست‌ها بر اساس هشتگ"""
        if not hashtags:
            return Post.objects.none()
        
        return Post.objects.filter(
            post_hashtags__hashtag__name__in=hashtags,
            is_deleted=False
        ).exclude(
            user=self.user
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes', 'comments', 'media_files'
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).distinct().order_by('-created_at')[:limit]
    
    def _get_trending_posts(self, limit):
        """پست‌های پرطرفدار"""
        return Post.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=3),
            is_deleted=False
        ).exclude(
            user=self.user
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            engagement=Count('likes') + Count('comments') * 2
        ).order_by('-engagement')[:limit]
    
    def _get_fallback_hashtags(self):
        """هشتگ‌های پیشنهادی بدون Ollama"""
        from apps.posts.models import Like
        
        liked_posts = Like.objects.filter(
            user=self.user
        ).values_list('post_id', flat=True)[:50]
        
        hashtags = PostHashtag.objects.filter(
            post_id__in=liked_posts
        ).values_list('hashtag__name', flat=True)
        
        from collections import Counter
        counter = Counter(hashtags)
        
        return [h for h, _ in counter.most_common(10)]
    
    def _rank_posts(self, posts, target_hashtags):
        """رتبه‌بندی پست‌ها"""
        target_set = set(target_hashtags)
        scored = []
        
        for post in posts:
            post_hashtags = set(
                PostHashtag.objects.filter(post=post).values_list('hashtag__name', flat=True)
            )
            
            common_count = len(target_set & post_hashtags)
            popularity = post.likes_count + (post.comments_count * 2)
            score = (common_count * 20) + min(popularity, 50)
            
            reasons = []
            if common_count > 0:
                common = list(target_set & post_hashtags)[:2]
                reasons.append(f"مشابه #{common[0]}")
            if post.likes_count > 20:
                reasons.append("محبوب در بین کاربران")
            if not reasons:
                reasons.append("پیشنهاد ویژه")
            
            scored.append({
                'post': post,
                'score': score,
                'reasons': reasons[:3]
            })
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored