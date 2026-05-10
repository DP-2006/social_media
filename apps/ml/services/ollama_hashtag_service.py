from django.core.cache import cache
class OllamaHashtagService:
    def __init__(self, user):
        self.user = user
    
    
    def get_recommended_hashtags(self, force_refresh=False):
        cache_key = f"hashtag_recommendations_{self.user.id}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        default_hashtags = [""]
        
        cache.set(cache_key, default_hashtags, 3600)
        return default_hashtags
