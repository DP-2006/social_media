from django.shortcuts import render

# Create your views here.
# apps/interactions/views.py

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.serializers import PostSerializer
from .services.explore_feed import ExploreFeedService


class ExploreFeedView(APIView):
    #GET /api/interactions/explore/?limit=20&offset=0&use_ollama=true
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = min(int(request.query_params.get('limit', 20)), 50)
        offset = int(request.query_params.get('offset', 0))
        use_ollama = request.query_params.get('use_ollama', 'true').lower() == 'true'
        
        explore_service = ExploreFeedService(request.user)
        
        feed_data = explore_service.get_explore_feed(
            limit=limit,
            offset=offset,
            use_ollama=use_ollama
        )
        
        serializer = PostSerializer(
            feed_data['posts'],
            many=True,
            context={'request': request}
        )
        
        response_posts = []
        for idx, post_data in enumerate(serializer.data):
            post_data['explore_score'] = feed_data['scores'][idx]
            post_data['explore_reasons'] = feed_data['reasons'][idx]
            response_posts.append(post_data)
        
        return Response({
            "success": True,
            "data": {
                "posts": response_posts,
                "used_hashtags": feed_data['used_hashtags'],
                "used_ollama": feed_data['used_ollama'],
                "pagination": {
                    "total_count": feed_data['total_count'],
                    "has_next": feed_data['has_next'],
                    "limit": limit,
                    "offset": offset
                }
            }
        }, status=status.HTTP_200_OK)