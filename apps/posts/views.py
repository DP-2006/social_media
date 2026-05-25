# apps/posts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.utils import timezone
from datetime import timedelta   

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


# class PostListCreateView(generics.ListCreateAPIView):
#     """
#     List all posts or create a new post
    
#     GET: Returns paginated list of posts
#     POST: Creates a new post with content and/or image
#     """
#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#     pagination_class = StandardPagination
    
#     def get_queryset(self):
#         queryset = Post.objects.filter(is_deleted=False).order_by('-created_at')
        
#         # Filter by user_id if provided
#         user_id = self.request.query_params.get('user_id')
#         if user_id:
#             queryset = queryset.filter(user_id=user_id)
        
#         # Filter by hashtag if provided
#         hashtag = self.request.query_params.get('hashtag')
#         if hashtag:
#             queryset = queryset.filter(post_hashtags__hashtag__name__icontains=hashtag)
        
#         return queryset.select_related('user', 'user__profile').prefetch_related('likes','comments')
    
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return PostCreateSerializer
#         return PostSerializer
    
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# apps/posts/views.py - فقط قسمت PostListCreateView رو اینطوری اصلاح کن

class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts or create a new post
    
    GET: Returns paginated list of posts (ONLY current user's posts)
    POST: Creates a new post with content and/or image
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            is_deleted=False,
            user=self.request.user  
        ).order_by('-created_at')
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            queryset = queryset.filter(post_hashtags__hashtag__name__icontains=hashtag)
        
        return queryset.select_related('user', 'user__profile').prefetch_related('likes', 'comments')
    
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



# ============================================
# VIDEO-SPECIFIC VIEWS
# ============================================

class VideoPostsListView(generics.ListAPIView):
    """
    List all video posts
    
    GET /api/posts/videos/
    
    Query params:
    - limit: Number of posts per page (default 20, max 50)
    - offset: Pagination offset (default 0)
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Post.objects.filter(
            video__isnull=False,
            is_deleted=False
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes', 'comments', 'media_files'
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


class TrendingVideosView(GenericAPIView):
    """
    Get trending videos based on likes and comments
    
    GET /api/posts/videos/trending/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        limit = min(int(request.GET.get('limit', 20)), 50)
        
        videos = Post.objects.filter(
            video__isnull=False,
            is_deleted=False,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).annotate(
            total_engagement=Count('likes') + Count('comments') * 2
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes', 'comments', 'media_files'
        ).order_by('-total_engagement', '-created_at')[:limit]
        
        serializer = PostSerializer(videos, many=True, context={'request': request})
        
        return Response({
            "success": True,
            "data": serializer.data,
            "count": len(videos)
        })


class SingleVideoView(GenericAPIView):
    """
    Get a single video post by ID
    
    GET /api/posts/videos/{post_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        post = get_object_or_404(
            Post, 
            id=post_id, 
            video__isnull=False,
            is_deleted=False
        )
        
        serializer = PostSerializer(post, context={'request': request})
        
        return Response({
            "success": True,
            "data": serializer.data
        })


# class FeedView(generics.ListAPIView):
#     """
#     Get feed posts (posts from people you follow)
    
#     GET /api/posts/feed/
#     """
#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = StandardPagination
    
#     def get_queryset(self):
#         from apps.follows.models import Follow
        
#         user = self.request.user
        
#         following_ids = Follow.objects.filter(
#             follower=user,
#             is_accepted=True
#         ).values_list('following_id', flat=True)
        
#         queryset = Post.objects.filter(
#             is_deleted=False,
#             user__in=list(following_ids) + [user.id]
#         ).order_by('-created_at')
        
#         return queryset.select_related('user', 'user__profile').prefetch_related('likes', 'comments')

class FeedView(generics.ListAPIView):
    """
    Get all posts sorted by popularity (likes count)
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            is_deleted=False
        ).order_by('-likes_count', '-created_at')  
        
        return queryset.select_related('user', 'user__profile').prefetch_related('likes', 'comments')



class DebugUserPostsView(GenericAPIView):
    """
    DEBUG: Show what user_id is being sent
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # چک کن کاربر وجود داره یا نه
        try:
            target_user = User.objects.get(id=user_id)
            target_exists = True
            target_username = target_user.username
        except User.DoesNotExist:
            target_exists = False
            target_username = None
        
        # پست‌های اون کاربر
        posts = Post.objects.filter(user_id=user_id, is_deleted=False) if target_exists else []
        
        return Response({
            "debug_info": {
                "user_id_sent_from_frontend": str(user_id),
                "current_logged_in_user_id": str(request.user.id),
                "current_logged_in_username": request.user.username,
                "target_user_exists": target_exists,
                "target_username": target_username,
                "is_same_user": str(request.user.id) == str(user_id)
            },
            "posts_count": posts.count(),
            "posts": [
                {
                    "id": str(p.id),
                    "content": p.content[:100],
                    "author_id": str(p.user.id),
                    "author_username": p.user.username
                }
                for p in posts[:5]
            ]
        })