# apps/posts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Post, Comment, Like, SavedPost
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, SavedPostSerializer,
    SavedPostListSerializer, LikeToggleResponseSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    SavePostResponseSerializer, CheckSavedStatusResponseSerializer,
    DeleteCommentResponseSerializer, PostIdSerializer, CommentIdSerializer,
    PostListQuerySerializer
)
from core.pagination import StandardPagination


class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts or create a new post
    
    GET: Returns paginated list of posts
    POST: Creates a new post with content and/or image
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_deleted=False).order_by('-created_at')
        
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by hashtag if provided
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            queryset = queryset.filter(post_hashtags__hashtag__name__icontains=hashtag)
        
        return queryset.select_related('user', 'user__profile').prefetch_related('likes','comments')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a post
    
    GET: Returns post details
    PUT/PATCH: Updates post content or image
    DELETE: Soft deletes the post
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostUpdateSerializer
        return PostSerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class LikeToggleView(GenericAPIView):
    """
    Toggle like status on a post
    
    POST: Like the post if not liked, unlike if already liked
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostIdSerializer
    
    def post(self, request, post_id):
        #cheake or sel Validate post_id
        serializer = self.get_serializer(data={'post_id': post_id})
        serializer.is_valid(raise_exception=True)
        
        post = get_object_or_404(Post, id=post_id, is_deleted=False)
        
        like = Like.objects.filter(user=request.user, post=post).first()
        
        if like:
            like.delete()
            response_data = {
                "success": True,
                "action": "unliked",
                "likes_count": post.likes.count()
            }
            return Response(response_data)
        else:
            Like.objects.create(user=request.user, post=post)
            response_data = {
                "success": True,
                "action": "liked",
                "likes_count": post.likes.count()
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    List comments for a post or create a new comment
    
    GET: Returns list of top-level comments for a post
    POST: Creates a new comment or reply
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id, 
            parent__isnull=True,
            is_deleted=False
        ).select_related('user', 'user__profile').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')  
        post = get_object_or_404(Post, id=post_id)
        
        parent_id = serializer.validated_data.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id, post=post)
            # Prevent nested replies (only one level deep)
            if parent.parent:
                raise serializers.ValidationError({"parent_id": "داداشمی مرامی کن جوابشو نده کوتاه بیا تو :"})
        
        serializer.save(user=self.request.user, post=post, parent=parent)


class CommentDeleteView(GenericAPIView):
    """
    Delete a comment
    
    DELETE: Soft deletes the comment (only owner or post owner can delete)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentIdSerializer
    
    def delete(self, request, comment_id):
        # Validate comment_id
        serializer = self.get_serializer(data={'comment_id': comment_id})
        serializer.is_valid(raise_exception=True)
        
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Check permissions: comment owner or post owner can delete
        if comment.user != request.user and comment.post.user != request.user:
            return Response(
                {"error": "اون که رفته دیگه هیچ وقت دیلیت نمیشه "}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.is_deleted = True
        comment.save()
        return Response({"success": True, "message": "تمیز برات برداشتم حاجی "}) # for delete 


class SavePostView(GenericAPIView):
    """
    Save or unsave a post
    
    POST: Saves the post if not saved, unsaves if already saved
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostIdSerializer
    
    def post(self, request, post_id):
        # Validate post_id
        serializer = self.get_serializer(data={'post_id': post_id})
        serializer.is_valid(raise_exception=True)
        
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
    """
    List all saved posts for the authenticated user
    
    GET: Returns paginated list of saved posts
    """
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
            'likes', 'comments'
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


class CheckSavedStatusView(GenericAPIView):
    """
    Check if a post is saved by the current user
    
    GET: Returns saved status and total save count for a post
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostIdSerializer
    
    def get(self, request, post_id):
        # Validate post_id
        serializer = self.get_serializer(data={'post_id': post_id})
        serializer.is_valid(raise_exception=True)
        
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


class UserPostsListView(generics.ListAPIView):
    """
    List all posts by a specific user
    
    GET: Returns paginated list of posts for a user
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Post.objects.filter(
            user_id=user_id,
            is_deleted=False
        ).select_related('user', 'user__profile').prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at')
    
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

class CommentUpdateView(GenericAPIView):
    """
    Update a comment (only comment owner can update)
    
    PATCH /api/posts/comments/{comment_id}/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentUpdateSerializer
    
    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)
        
        if comment.user != request.user:
            return Response({
                "success": False,
                "error": "شما اجازه ویرایش این کامنت را ندارید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_comment = serializer.save()
        
        return Response({
            "success": True,
            "message": "کامنت با موفقیت ویرایش شد",
            "data": CommentSerializer(updated_comment, context={'request': request}).data
        }, status=status.HTTP_200_OK)

class CommentDetailView(GenericAPIView):
    """
    Update or delete a comment
    DELETE: Soft deletes the comment
    PATCH: Updates the comment text
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)
        
        if comment.user != request.user:
            return Response({
                "success": False,
                "error": "شما اجازه ویرایش این کامنت را ندارید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_comment = serializer.save()
        
        return Response({
            "success": True,
            "message": "کامنت با موفقیت ویرایش شد",
            "data": CommentSerializer(updated_comment, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.user != request.user and comment.post.user != request.user:
            return Response({
                "success": False,
                "error": "شما اجازه حذف این کامنت را ندارید"
            }, status=status.HTTP_403_FORBIDDEN)
        
        comment.is_deleted = True
        comment.save()
        
        return Response({
            "success": True, 
            "message": "کامنت با موفقیت حذف شد"
        }, status=status.HTTP_200_OK)
