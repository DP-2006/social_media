# apps/search/services/simple_search.py

import re
from .base_search import BaseSearchService


class SimpleSearchService(BaseSearchService):
    
    def search_all(self, query, limit=20, offset=0):
        # استخراج هشتگ‌ها از متن
        hashtags = re.findall(r'#([a-zA-Z0-9_\u0600-\u06FF]+)', query)
        results = {
            'query': query,
            'source': 'simple',
            'smart_keywords': hashtags,
            'users': self.search_users(query, limit=5),
            'hashtags': self.search_hashtags(query, limit=10),
            'posts': self.search_posts(query, hashtags, limit=limit),
        }
        return results
    
    def extract_keywords(self, query):
        """استخراج کلمات کلیدی ساده"""
        stop_words = {'و', 'به', 'از', 'برای', 'یک', 'این', 'آن', 'با', 'تا', 'در'}
        
        words = re.findall(r'[a-zA-Z0-9_\u0600-\u06FF]+', query)
        keywords = [w.lower() for w in words if w.lower() not in stop_words and len(w) > 2]
        
        return keywords[:10]