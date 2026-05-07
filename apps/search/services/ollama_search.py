# apps/search/services/ollama_search.py

import re
import logging
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.hashtags.models import Hashtag

from .base_search import BaseSearchService

logger = logging.getLogger(__name__)
User = get_user_model()


class OllamaSearchService(BaseSearchService):
    def __init__(self, request_user=None):
        super().__init__(request_user)
        self._ollama_client = None
        self.use_ollama = getattr(settings, 'SEARCH_USE_OLLAMA', True)
    
    def _get_ollama_client(self):
        if not self.use_ollama:
            return None
        
        if self._ollama_client is None:
            try:
                from apps.ml.ollama_client import OllamaClient
                self._ollama_client = OllamaClient()
            except ImportError:
                logger.warning("OllamaClient not found")
                self._ollama_client = None
        return self._ollama_client
    
    def search_all(self, query, limit=20, offset=0):
        cache_key = f"ollama_search_{hash(query)}_{offset}_{limit}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        smart_keywords = self.extract_keywords(query)
        
        results = {
            'query': query,
            'source': 'ollama' if smart_keywords else 'simple',
            'smart_keywords': smart_keywords,
            'users': self.search_users(query, limit=5),
            'hashtags': self.search_hashtags(query, limit=10),
            'posts': self.search_posts(query, smart_keywords, limit=limit),
        }
        
        cache.set(cache_key, results, 60 * 5)
        
        return results
    
    def extract_keywords(self, query):
        ollama = self._get_ollama_client()
        
        if not ollama or not self.use_ollama:
            return self._simple_extract(query)
        
        cache_key = f"search_keywords_{hash(query)}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        prompt = f"""
        متن جستجوی کاربر: "{query}"
        
        3 تا 5 کلمه کلیدی یا هشتگ مرتبط با این متن پیشنهاد بده.
        فقط کلمات را برگردان، بدون توضیح اضافی.
        
        مثال:
        "عکس طبیعت زیبا" -> nature, landscape, photography
        
        حالا برای "{query}" خروجی را بده:
        """
        
        try:
            result = ollama.generate(prompt, temperature=0.5, max_tokens=100)
            
            if result.get('success'):
                response = result.get('response', '')
                keywords = re.findall(r'[a-zA-Z0-9_\u0600-\u06FF]+', response)
                keywords = [k.lower() for k in keywords if len(k) > 2][:5]
                
                cache.set(cache_key, keywords, 60 * 60)
                return keywords
            
            return self._simple_extract(query)
            
        except Exception as e:
            logger.error(f"Ollama keyword extraction error: {e}")
            return self._simple_extract(query)
    
    def _simple_extract(self, query):
        stop_words = {'و', 'به', 'از', 'برای', 'یک', 'این', 'آن', 'با', 'تا', 'در'}
        
        words = re.findall(r'[a-zA-Z0-9_\u0600-\u06FF]+', query)
        keywords = [w.lower() for w in words if w.lower() not in stop_words and len(w) > 2]
        
        return keywords[:5]
    
    def search_hashtags(self, query, limit=20):
        """جستجوی هشتگ‌ها - مستقیماً از کلاس پایه استفاده می‌کند"""
        return super().search_hashtags(query, limit)
    
    def search_users(self, query, limit=20):
        """جستجوی کاربران با قابلیت بلاک"""
        return super().search_users(query, limit)
    
    def search_suggestions(self, query, limit=10):
        """پیشنهادات لحظه‌ای جستجو (autocomplete)"""
        
        if not query or len(query) < 2:
            return {'users': [], 'hashtags': []}
        
        cache_key = f"search_suggestions_{hash(query)}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        suggestions = {
            'users': [],
            'hashtags': []
        }
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__display_name__icontains=query)
        )[:5]
        
        for user in users:
            profile = getattr(user, 'profile', None)
            suggestions['users'].append({
                'type': 'user',
                'text': user.username,
                'display': profile.display_name if profile else user.username,
                'image': profile.profile_image.url if profile and profile.profile_image else None,
                'id': str(user.id)
            })
        
        hashtags = Hashtag.objects.filter(
            name__icontains=query.replace('#', '')
        ).order_by('-usage_count')[:5]
        
        for tag in hashtags:
            suggestions['hashtags'].append({
                'type': 'hashtag',
                'text': f"#{tag.name}",
                'count': tag.usage_count,
                'name': tag.name
            })
        
        cache.set(cache_key, suggestions, 60 * 10)
        
        return suggestions