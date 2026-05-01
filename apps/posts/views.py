
# apps/posts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
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
    
    def perform_update(self, serializer):
        post = self.get_object()
        if post.user != self.request.user:
            raise PermissionDenied("You can only edit your own post")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own post")
        instance.delete()


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        serializer.context['target_post'] = post
        
        parent_id = serializer.initial_data.get('parent')
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            if parent_comment.post.id != post.id:
                raise PermissionDenied("Comment parent must belong to this post")
        
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.all()
    
    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You can only edit your own comment")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own comment")
        instance.delete()


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
                'message': 'Post liked successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'already_liked',
            'message': 'You have already liked this post'
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        deleted, _ = Like.objects.filter(post=post, user=request.user).delete()
        
        if deleted:
            return Response({
                'status': 'unliked',
                'message': 'Post unliked successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'not_liked',
            'message': 'You have not liked this post'
        }, status=status.HTTP_404_NOT_FOUND)