# apps/posts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Post, Comment, Like, SavedPost
from .serializers import PostSerializer, CommentSerializer, SavedPostSerializer, SavePostResponseSerializer
from core.pagination import StandardPagination  
from apps.blocks.views import BlockedUsersMixin 



class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Post.objects.filter(is_deleted=False).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(is_deleted=False)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()



class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)
        
        like = Like.objects.filter(user=request.user, post=post).first()
        
        if like:
            like.delete()
            return Response({
                "success": True,
                "action": "unliked",
                "likes_count": post.likes.count()
            })
        else:
            Like.objects.create(user=request.user, post=post)
            return Response({
                "success": True,
                "action": "liked",
                "likes_count": post.likes.count()
            }, status=status.HTTP_201_CREATED)



class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id, parent__isnull=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        parent_id = self.request.data.get('parent_id')
        
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id, post=post)
            if parent.parent:
                return Response({"error": "حداکثر فقط یک سطح ریپلای مجاز است"}, status=400)
        
        serializer.save(user=self.request.user, post=post, parent=parent)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.user != request.user and comment.post.user != request.user:
            return Response({"error": "شما اجازه حذف این کامنت را ندارید"}, status=403)
        
        comment.delete()
        return Response({"success": True, "message": "کامنت حذف شد"})



class SavePostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)
        
        saved = SavedPost.objects.filter(user=request.user, post=post).first()
        
        if saved:
            saved.delete()
            saved_count = SavedPost.objects.filter(user=request.user).count()
            
            return Response({
                "success": True,
                "action": "unsaved",
                "message": "پست از لیست ذخیره شده‌ها حذف شد",
                "saved_count": saved_count
            }, status=status.HTTP_200_OK)
        else:
            SavedPost.objects.create(user=request.user, post=post)
            saved_count = SavedPost.objects.filter(user=request.user).count()
            
            return Response({
                "success": True,
                "action": "saved",
                "message": "پست با موفقیت ذخیره شد",
                "saved_count": saved_count
            }, status=status.HTTP_201_CREATED)


class SavedPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination  
    
    def get_queryset(self):
        return Post.objects.filter(
            saved_by_users__user=self.request.user,
            is_deleted=False
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes', 'comments', 'media_files'
        ).order_by('-saved_by_users__saved_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response({
                "success": True,
                "data": serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        })


class CheckSavedStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
        saved_count = SavedPost.objects.filter(post=post).count()
        
        return Response({
            "success": True,
            "data": {
                "is_saved": is_saved,
                "saved_count": saved_count
            }
        })