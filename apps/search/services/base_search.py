# apps/search/services/base_search.py

from abc import ABC, abstractmethod
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from apps.posts.models import Post
from apps.hashtags.models import Hashtag

User = get_user_model()


class BaseSearchService(ABC):
    
    def __init__(self, request_user=None):
        self.request_user = request_user
    
    @abstractmethod
    def search_all(self, query, limit=20, offset=0):
        pass
    
    @abstractmethod
    def extract_keywords(self, query):
        pass
    
    def search_users(self, query, limit=20):
        if not query or len(query) < 2:
            return []
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(phone__icontains=query) |
            Q(profile__display_name__icontains=query)
        ).select_related('profile')[:limit]
        
        results = []
        for user in users:
            profile = getattr(user, 'profile', None)
            results.append({
                'id': str(user.id),
                'username': user.username,
                'display_name': profile.display_name if profile else user.username,
                'profile_image': profile.profile_image.url if profile and profile.profile_image else None,
                'bio': profile.bio if profile else '',
            })
        
        return results
    
    def search_hashtags(self, query, limit=20):
        if not query or len(query) < 2:
            return []
        
        clean_query = query.replace('#', '').lower()
        
        hashtags = Hashtag.objects.filter(
            name__icontains=clean_query
        ).order_by('-usage_count')[:limit]
        
        return [
            {
                'name': h.name,
                'usage_count': h.usage_count,
            }
            for h in hashtags
        ]
    
    def search_posts(self, query, keywords=None, limit=20):
        if not query and not keywords:
            return []
        
        search_q = Q()
        
        if query:
            search_q |= Q(content__icontains=query)
        
        if keywords:
            search_q |= Q(post_hashtags__hashtag__name__in=keywords)
        
        posts = Post.objects.filter(
            search_q,
            is_deleted=False
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes', 'comments', 'media_files'
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).distinct().order_by('-created_at')[:limit]
        
        from apps.posts.serializers import PostSerializer
        return PostSerializer(posts, many=True, context={'request': None}).data