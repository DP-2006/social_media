from django.shortcuts import render

# Create your views here.
# apps/hashtags/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Hashtag, PostHashtag
from .serializers import HashtagSerializer, TrendingHashtagSerializer
from core.pagination import StandardPagination
from django.db import models

class HashtagViewSet(viewsets.ModelViewSet):
    serializer_class = HashtagSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    lookup_field = 'name'

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        if query:
            return Hashtag.objects.filter(name__icontains=query)
        return Hashtag.objects.all()

    @action(detail=False, methods=['get'])
    def trending(self, request):
        hashtags = Hashtag.objects.order_by('-usage_count')[:20]
        serializer = TrendingHashtagSerializer(hashtags, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, name=None):
        hashtag = self.get_object()
        post_hashtags = PostHashtag.objects.filter(hashtag=hashtag).select_related('post', 'post__user')
        
        # Pagination
        page = self.paginate_queryset(post_hashtags)
        if page is not None:
            from apps.posts.serializers import PostSerializer
            posts = [ph.post for ph in page]
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        from apps.posts.serializers import PostSerializer
        posts = [ph.post for ph in post_hashtags]
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


