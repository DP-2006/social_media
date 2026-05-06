# apps/search/views.py

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from .services.ollama_search import OllamaSearchService
from .services.simple_search import SimpleSearchService
from .serializers import (
    SearchResultSerializer,
    SearchSuggestionsSerializer,
    SearchConfigSerializer,
    UserSearchSerializer,
    HashtagSearchSerializer
)


def get_search_service(request_user=None):
    use_ollama = getattr(settings, 'SEARCH_USE_OLLAMA', True)
    
    if use_ollama:
        return OllamaSearchService(request_user)
    else:
        return SimpleSearchService(request_user)


class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                "success": False,
                "error": "لطفاً عبارت جستجو را وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(query) < 2:
            return Response({
                "success": False,
                "error": "عبارت جستجو باید حداقل ۲ کاراکتر باشد"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        limit = min(int(request.query_params.get('limit', 20)), 50)
        offset = int(request.query_params.get('offset', 0))
        force_simple = request.query_params.get('force_simple', 'false').lower() == 'true'
        
        if force_simple:
            search_service = SimpleSearchService(request.user)
        else:
            search_service = get_search_service(request.user)
        
        results = search_service.search_all(query, limit, offset)
        serializer = SearchResultSerializer(results)
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class SearchByUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, username=None):
        if username:
            query_username = username.replace('@', '')
        else:
            query_username = request.query_params.get('username', '').strip()
        
        if not query_username:
            return Response({
                "success": False,
                "error": "لطفاً username را وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        search_service = get_search_service(request.user)
        user_data = search_service.search_users_exact(query_username)
        
        if not user_data:
            return Response({
                "success": False,
                "error": f"کاربری با username '{query_username}' یافت نشد"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSearchSerializer(data=user_data[0])
        serializer.is_valid()
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class SearchUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        if not query:
            return Response({
                "success": False,
                "error": "لطفاً عبارت جستجو را وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(query) < 2:
            return Response({
                "success": False,
                "error": "عبارت جستجو باید حداقل ۲ کاراکتر باشد"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        search_service = get_search_service(request.user)
        users = search_service.search_users(query, limit)
        serializer = UserSearchSerializer(users, many=True)
        
        return Response({
            "success": True,
            "data": {
                "count": len(users),
                "users": serializer.data
            }
        }, status=status.HTTP_200_OK)


class SearchPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = min(int(request.query_params.get('limit', 20)), 50)
        use_ollama = request.query_params.get('use_ollama', 'true').lower() == 'true'
        
        if not query:
            return Response({
                "success": False,
                "error": "لطفاً عبارت جستجو را وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if use_ollama and getattr(settings, 'SEARCH_USE_OLLAMA', True):
            search_service = OllamaSearchService(request.user)
        else:
            search_service = SimpleSearchService(request.user)
        
        smart_keywords = []
        if use_ollama and hasattr(search_service, 'extract_keywords'):
            smart_keywords = search_service.extract_keywords(query)
        
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


class SearchHashtagsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        if not query:
            return Response({
                "success": False,
                "error": "لطفاً عبارت جستجو را وارد کنید"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        search_service = get_search_service(request.user)
        hashtags = search_service.search_hashtags(query, limit)
        serializer = HashtagSearchSerializer(hashtags, many=True)
        
        return Response({
            "success": True,
            "data": {
                "count": len(hashtags),
                "hashtags": serializer.data
            }
        }, status=status.HTTP_200_OK)


class SearchSuggestionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
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
        
        serializer = SearchSuggestionsSerializer(suggestions)
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class SearchConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config_data = {
            "use_ollama": getattr(settings, 'SEARCH_USE_OLLAMA', True),
            "ollama_timeout": getattr(settings, 'SEARCH_OLLAMA_TIMEOUT', 30),
        }
        
        serializer = SearchConfigSerializer(config_data)
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)