# apps/ml/services/ollama_hashtag_service.py

import json
import logging
import re
from collections import Counter
from django.core.cache import cache
from django.db.models import Count

from apps.posts.models import Post, Like
from apps.follows.models import Follow
from apps.hashtags.models import PostHashtag
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class OllamaHashtagService:
    """
    سرویس استخراج هشتگ‌های پیشنهادی با استفاده از Ollama
    این کلاس در اپ ml قرار دارد و توسط سایر اپ‌ها استفاده می‌شود
    """
    
    def __init__(self, user):
        self.user = user
        self._ollama_client = None
    
    def _get_ollama_client(self):
        """دریافت کلاینت Ollama"""
        if self._ollama_client is None:
            self._ollama_client = OllamaClient()
        return self._ollama_client
    
    def get_recommended_hashtags(self, force_refresh=False):
        """
        دریافت هشتگ‌های پیشنهادی از Ollama
        با کش 24 ساعته
        """
        cache_key = f"ollama_hashtags_{self.user.id}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Using cached hashtags for user {self.user.id}")
                return cached
        
        # جمع‌آوری داده‌های کاربر
        user_data = self._collect_user_data()
        
        # دریافت از Ollama یا fallback
        recommended_hashtags = self._get_from_ollama(user_data)
        
        # ذخیره در کش
        cache.set(cache_key, recommended_hashtags, 60 * 60 * 24)  # 24 ساعت
        
        return recommended_hashtags
    
    def _collect_user_data(self):
        """جمع‌آوری داده‌های کاربر برای ارسال به Ollama"""
        
        # هشتگ‌های پراستفاده کاربر
        user_hashtags = PostHashtag.objects.filter(
            post__user=self.user
        ).values('hashtag__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # پست‌هایی که لایک کرده
        liked_posts = Like.objects.filter(
            user=self.user
        ).select_related('post')[:10]
        
        liked_hashtags = []
        for like in liked_posts:
            tags = PostHashtag.objects.filter(
                post=like.post
            ).values_list('hashtag__name', flat=True)
            liked_hashtags.extend(tags)
        
        # بیوگرافی کاربر
        bio = ""
        if hasattr(self.user, 'profile') and self.user.profile:
            bio = self.user.profile.bio or ""
        
        return {
            "bio": bio,
            "user_hashtags": [h['hashtag__name'] for h in user_hashtags],
            "liked_hashtags": list(set(liked_hashtags))[:20],
            "posts_count": Post.objects.filter(user=self.user).count(),
            "followers_count": Follow.objects.filter(following=self.user).count()
        }
    
    def _get_from_ollama(self, user_data):
        """ارسال به Ollama و دریافت هشتگ‌های پیشنهادی"""
        
        ollama = self._get_ollama_client()
        
        if not ollama:
            return self._fallback_recommendation(user_data)
        
        prompt = f"""
        شما یک سیستم پیشنهاددهنده محتوا هستید. بر اساس اطلاعات کاربر زیر، 
        5 تا 10 هشتگ که کاربر به آنها علاقه دارد را پیشنهاد بده.
        
        اطلاعات کاربر:
        - بیوگرافی: {user_data.get('bio', 'ندارد')}
        - هشتگ‌های خود کاربر: {user_data.get('user_hashtags', [])}
        - هشتگ‌های پست‌هایی که لایک کرده: {user_data.get('liked_hashtags', [])}
        - تعداد پست: {user_data.get('posts_count', 0)}
        - تعداد فالوور: {user_data.get('followers_count', 0)}
        
        فقط یک لیست از هشتگ‌ها برگردان. بدون هیچ توضیح اضافی.
        
        مثال خروجی:
        ["nature", "travel", "photography", "adventure", "sunset"]
        """
        
        try:
            result = ollama.generate(prompt, temperature=0.5, max_tokens=200)
            
            if result.get('success'):
                response_text = result.get('response', '')
                hashtags = self._extract_hashtags_from_text(response_text)
                if hashtags:
                    return hashtags
            
            return self._fallback_recommendation(user_data)
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_recommendation(user_data)
    
    def _extract_hashtags_from_text(self, text):
        """استخراج هشتگ از متن پاسخ Ollama"""
        try:
            if text.strip().startswith('['):
                hashtags = json.loads(text)
                if isinstance(hashtags, list):
                    return [h.replace('#', '').strip() for h in hashtags]
        except:
            pass
        
        hashtags = re.findall(r'#?([a-zA-Z0-9_\u0600-\u06FF]+)', text)
        return [h for h in hashtags if len(h) > 2][:10]
    
    def _fallback_recommendation(self, user_data):
        """روش جایگزین بدون Ollama"""
        
        all_hashtags = (
            user_data.get('user_hashtags', []) + 
            user_data.get('liked_hashtags', [])
        )
        
        counter = Counter(all_hashtags)
        return [h for h, _ in counter.most_common(10)]
    
    def get_cached_hashtags(self):
        """دریافت هشتگ‌های کش شده"""
        cache_key = f"ollama_hashtags_{self.user.id}"
        return cache.get(cache_key, [])
    
    def extract_hashtags_from_query(self, query):
        """
        استخراج هشتگ‌های مرتبط از متن جستجو (برای search)
        """
        ollama = self._get_ollama_client()
        
        if not ollama:
            return []
        
        prompt = f"""
        متن جستجوی کاربر: "{query}"
        
        3 تا 5 هشتگ مرتبط با این متن پیشنهاد بده.
        فقط هشتگ‌ها را برگردان، بدون # و بدون توضیح.
        
        مثال: "عکس طبیعت زیبا" -> nature, landscape, photography
        """
        
        try:
            result = ollama.generate(prompt, temperature=0.5, max_tokens=100)
            
            if result.get('success'):
                response = result.get('response', '')
                hashtags = re.findall(r'[a-zA-Z0-9_\u0600-\u06FF]+', response)
                return [h.lower() for h in hashtags if len(h) > 2][:5]
            
            return []
            
        except Exception as e:
            logger.error(f"Ollama search extraction error: {e}")
            return []