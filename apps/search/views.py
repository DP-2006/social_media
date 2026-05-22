# apps/search/views.py
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.conf import settings

from .services.ollama_search import OllamaSearchService
from .services.simple_search import SimpleSearchService
from .serializers import (
    SearchResultSerializer,
    SearchSuggestionsSerializer,
    SearchConfigSerializer,
    UserSearchSerializer,
    HashtagSearchSerializer,
    GlobalSearchQuerySerializer,
    SearchPostsQuerySerializer,
    SearchByUsernameSerializer,
    SearchUsersQuerySerializer,
    SearchHashtagsQuerySerializer,
    SearchSuggestionsQuerySerializer,
    UsersSearchResponseSerializer,
    HashtagsSearchResponseSerializer,
    PostsSearchResponseSerializer,
    GlobalSearchResponseSerializer,
    SearchSuggestionsResponseSerializer,
    SearchConfigResponseSerializer
)


def get_search_service(request_user=None):  
    """Factory function to get the appropriate search service"""
    use_ollama = getattr(settings, 'SEARCH_USE_OLLAMA', True)
    
    if use_ollama:
        return OllamaSearchService(request_user)
    else:
        return SimpleSearchService(request_user)


class GlobalSearchView(GenericAPIView):
    """
    Global search across users, hashtags, and posts
    
    GET: Returns combined search results from all content types
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GlobalSearchQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data.get('q')
        limit = serializer.validated_data.get('limit', 20)
        offset = serializer.validated_data.get('offset', 0)
        force_simple = serializer.validated_data.get('force_simple', False)
        
        if force_simple:
            search_service = SimpleSearchService(request.user)
        else:
            search_service = get_search_service(request.user)
        
        results = search_service.search_all(query, limit, offset)
        response_serializer = SearchResultSerializer(results)
        
        return Response({
            "success": True,
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)


class SearchByUsernameView(GenericAPIView):
    """
    Search for a user by exact username
    
    GET: Returns user data for the specified username
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchByUsernameSerializer
    
    def get(self, request, username=None):
        if username:
            # If username is in URL path
            data = {'username': username}
        else:
            # If username is in query parameters
            data = {'username': request.query_params.get('username', '')}
        
        # Validate username
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        query_username = serializer.validated_data['username']
        
        search_service = get_search_service(request.user)
        user_data = search_service.search_users_exact(query_username)
        
        if not user_data:
            return Response({
                "success": False,
                "error": f"کاربری با username '{query_username}' یافت نشد"
            }, status=status.HTTP_404_NOT_FOUND)
        
        result_serializer = UserSearchSerializer(data=user_data[0])
        result_serializer.is_valid()
        
        return Response({
            "success": True,
            "data": result_serializer.data
        }, status=status.HTTP_200_OK)


class SearchUsersView(GenericAPIView):
    """
    Search for users by username or display name
    
    GET: Returns list of users matching the search query
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchUsersQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['q']
        limit = serializer.validated_data.get('limit', 20)
        
        search_service = get_search_service(request.user)
        users = search_service.search_users(query, limit)
        result_serializer = UserSearchSerializer(users, many=True)
        
        return Response({
            "success": True,
            "data": {
                "count": len(users),
                "users": result_serializer.data
            }
        }, status=status.HTTP_200_OK)


class SearchPostsView(GenericAPIView):
    """
    Search for posts by content
    
    GET: Returns list of posts matching the search query
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchPostsQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['q']
        limit = serializer.validated_data.get('limit', 20)
        use_ollama = serializer.validated_data.get('use_ollama', True)
        
        smart_keywords = []
        
        if use_ollama and getattr(settings, 'SEARCH_USE_OLLAMA', True):
            search_service = OllamaSearchService(request.user)
            if hasattr(search_service, 'extract_keywords'):
                smart_keywords = search_service.extract_keywords(query)
        else:
            search_service = SimpleSearchService(request.user)
        
        posts = search_service.search_posts(query, smart_keywords, limit)
        
        return Response({
            "success": True,
            "data": {
                "query": query,
                "smart_keywords": smart_keywords,
                "used_ollama": use_ollama and bool(smart_keywords),
                "count": len(posts),
                "posts": posts
            }
        }, status=status.HTTP_200_OK)


class SearchHashtagsView(GenericAPIView):
    """
    Search for hashtags by name
    
    GET: Returns list of hashtags matching the search query
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchHashtagsQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['q']
        limit = serializer.validated_data.get('limit', 20)
        
        search_service = get_search_service(request.user)
        hashtags = search_service.search_hashtags(query, limit)
        result_serializer = HashtagSearchSerializer(hashtags, many=True)
        
        return Response({
            "success": True,
            "data": {
                "count": len(hashtags),
                "hashtags": result_serializer.data
            }
        }, status=status.HTTP_200_OK)


class SearchSuggestionsView(GenericAPIView):
    """
    Get search suggestions as user types
    
    GET: Returns real-time search suggestions for users and hashtags
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchSuggestionsQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['q']
        
        # If query is less than 2 characters, return empty results
        if len(query) < 2:
            return Response({
                "success": True,
                "data": {
                    "users": [],
                    "hashtags": []
                }
            }, status=status.HTTP_200_OK)
        
        search_service = get_search_service(request.user)
        
        if hasattr(search_service, 'search_suggestions'):
            suggestions = search_service.search_suggestions(query)
        else:
            suggestions = {'users': [], 'hashtags': []}
        
        result_serializer = SearchSuggestionsSerializer(suggestions)
        
        return Response({
            "success": True,
            "data": result_serializer.data
        }, status=status.HTTP_200_OK)


class SearchConfigView(GenericAPIView):
    """
    Get search configuration settings
    
    GET: Returns current search configuration including Ollama settings
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SearchConfigSerializer
    
    def get(self, request):
        config_data = {
            "use_ollama": getattr(settings, 'SEARCH_USE_OLLAMA', True),
            "ollama_timeout": getattr(settings, 'SEARCH_OLLAMA_TIMEOUT', 30),
            "ollama_model": getattr(settings, 'SEARCH_OLLAMA_MODEL', 'gemma3:27b'),
            "min_query_length": getattr(settings, 'SEARCH_MIN_QUERY_LENGTH', 2),
            "max_results_per_page": getattr(settings, 'SEARCH_MAX_RESULTS_PER_PAGE', 50),
        }
        
        result_serializer = self.get_serializer(data=config_data)
        result_serializer.is_valid()
        
        return Response({
            "success": True,
            "data": result_serializer.data
        }, status=status.HTTP_200_OK)


class TrendingSearchesView(GenericAPIView):
    """
    Get trending search queries
    
    GET: Returns list of trending search queries
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = min(int(request.query_params.get('limit', 10)), 20)
        
        search_service = get_search_service(request.user)
        
        if hasattr(search_service, 'get_trending_searches'):
            trending = search_service.get_trending_searches(limit)
        else:
            trending = []
        
        return Response({
            "success": True,
            "data": {
                "trending": trending,
                "count": len(trending)
            }
        }, status=status.HTTP_200_OK)


class ClearSearchHistoryView(GenericAPIView):
    """
    Clear user's search history
    
    DELETE: Clears all search history for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        search_service = get_search_service(request.user)
        
        if hasattr(search_service, 'clear_history'):
            search_service.clear_history()
        
        return Response({
            "success": True,
            "message": "تاریخچه جستجو با موفقیت پاک شد"
        }, status=status.HTTP_200_OK)


class RecentSearchesView(GenericAPIView):
    """
    Get user's recent searches
    
    GET: Returns list of recent search queries by the user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = min(int(request.query_params.get('limit', 10)), 20)
        
        search_service = get_search_service(request.user)
        
        if hasattr(search_service, 'get_recent_searches'):
            recent = search_service.get_recent_searches(limit)
        else:
            recent = []
        
        return Response({
            "success": True,
            "data": {
                "recent_searches": recent,
                "count": len(recent)
            }
        }, status=status.HTTP_200_OK)


class AdvancedSearchView(GenericAPIView):
    """
    Advanced search with filters
    
    POST: Performs advanced search with various filters
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('q', '').strip()
        content_type = request.data.get('content_type', 'all')  # all, users, posts, hashtags
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        min_likes = request.data.get('min_likes')
        hashtags = request.data.get('hashtags', [])
        limit = min(int(request.data.get('limit', 20)), 50)
        
        if not query and not hashtags:
            return Response({
                "success": False,
                "error": "لطفاً حداقل یک عبارت جستجو یا هشتگ وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        search_service = get_search_service(request.user)
        
        results = search_service.advanced_search(
            query=query,
            content_type=content_type,
            date_from=date_from,
            date_to=date_to,
            min_likes=min_likes,
            hashtags=hashtags,
            limit=limit
        )
        
        return Response({
            "success": True,
            "data": results
        }, status=status.HTTP_200_OK)