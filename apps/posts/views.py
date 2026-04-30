
# apps/posts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all()


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')
    
    # mistake user can replay anouther coment in some anouther post 
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.all()


class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        if created:
            return Response({
                'status': 'liked',
                'message': 'پست با موفقیت لایک شد'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'already_liked',
            'message': 'شما قبلاً این پست را لایک کرده‌اید'
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        deleted, _ = Like.objects.filter(post=post, user=request.user).delete()
        
        if deleted:
            return Response({
                'status': 'unliked',
                'message': 'لایک پست حذف شد'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'not_liked',
            'message': 'شما این پست را لایک نکرده‌اید'
        }, status=status.HTTP_400_BAD_REQUEST)
