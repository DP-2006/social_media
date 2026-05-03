from django.shortcuts import render

# Create your views here.
# apps/search/views.py

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from .services.ollama_search import OllamaSearchService
from .services.simple_search import SimpleSearchService


def get_search_service(request_user=None):
    """دریافت سرویس جستجو بر اساس تنظیمات"""
    use_ollama = getattr(settings, 'SEARCH_USE_OLLAMA', True)
    
    if use_ollama:
        return OllamaSearchService(request_user)
    else:
        return SimpleSearchService(request_user)


class GlobalSearchView(APIView):
    """
    جستجوی جهانی
    GET /api/search/?q=متن&limit=20&force_simple=false
    """
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
        
        # انتخاب سرویس
        if force_simple:
            search_service = SimpleSearchService(request.user)
        else:
            search_service = get_search_service(request.user)
        
        results = search_service.search_all(query, limit, offset)
        
        return Response({
            "success": True,
            "data": results
        }, status=status.HTTP_200_OK)


class SearchConfigView(APIView):
    """
    دریافت/تنظیم تنظیمات جستجو
    GET /api/search/config/
    POST /api/search/config/ (با body: {"use_ollama": true/false})
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            "success": True,
            "data": {
                "use_ollama": getattr(settings, 'SEARCH_USE_OLLAMA', True),
                "ollama_timeout": getattr(settings, 'SEARCH_OLLAMA_TIMEOUT', 30),
            }
        })
    
    def post(self, request):
        # فقط ادمین‌ها می‌توانند تغییر دهند
        if not request.user.is_staff:
            return Response({
                "success": False,
                "error": "شما اجازه تغییر تنظیمات را ندارید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        use_ollama = request.data.get('use_ollama')
        
        if use_ollama is not None:
            # ذخیره در cache یا database
            cache_key = "search_use_ollama"
            cache.set(cache_key, use_ollama, 60 * 60 * 24)
        
        return Response({
            "success": True,
            "message": "تنظیمات با موفقیت ذخیره شد",
            "data": {
                "use_ollama": use_ollama if use_ollama is not None else getattr(settings, 'SEARCH_USE_OLLAMA', True)
            }
        })