from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.interactions.services.weight_calculator import WeightCalculator
from rest_framework import status
from django.utils import timezone
from apps.posts.models import Post
from apps.follows.models import Follow
from datetime import timedelta  
       
from typing import Dict
from apps.posts.models import Post
from apps.follows.models import Follow
from apps.interactions.models import UserPostEngagement


class EngagementMixin:
    
    def get_or_create_engagement(self, user, post_id):
        from apps.interactions.models import UserPostEngagement
        engagement, created = UserPostEngagement.objects.get_or_create(
            user=user, post_id=post_id
        )
        return engagement, created
    
    def update_engagement_and_recalculate(self, engagement, **kwargs):
        for key, value in kwargs.items():
            if hasattr(engagement, key):
                setattr(engagement, key, value)
        engagement.save()
        
        
        calculator = WeightCalculator(engagement.user, engagement.post)
        weight = calculator.calculate()
        return weight


class TrackPostView(EngagementMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        duration_ms = request.data.get('duration_ms')
        if not duration_ms:
            return Response({'error': 'duration_ms required'}, status=400)
        
        engagement, created = self.get_or_create_engagement(request.user, post_id)
        
        update_data = {
            'view_duration_ms': duration_ms,
            'scroll_depth': request.data.get('scroll_depth', 0),
            'visibility_ratio': request.data.get('visibility_ratio', 1.0)
        }
        
        weight = self.update_engagement_and_recalculate(engagement, **update_data)
        
        return Response({
            'status': 'tracked',
            'post_id': post_id,
            'calculated_weight': round(weight, 4),
            'confidence': getattr(engagement, 'confidence_score', 0.5)
        })
    
    def patch(self, request, post_id):
        engagement, _ = self.get_or_create_engagement(request.user, post_id)
        
        update_data = {}
        field_mapping = {
            'like': 'liked_at',
            'save': 'saved_at', 
            'share': 'shared_at',
            'comment': 'commented_at'
        }
        
        for input_field, model_field in field_mapping.items():
            if input_field in request.data:
                update_data[model_field] = timezone.now() if request.data[input_field] else None
        
        if not update_data:
            return Response({'error': 'No valid fields'}, status=400)
        
        weight = self.update_engagement_and_recalculate(engagement, **update_data)
        
        return Response({'status': 'updated', 'weight': round(weight, 4)})


class BulkTrackView(EngagementMixin, GenericAPIView):
    
    permission_classes = [IsAuthenticated]
    max_batch_size = 50
    
    def post(self, request):
        events = request.data.get('events', [])
        
        if not events:
            return Response({'error': 'events list required'}, status=400)
        
        if len(events) > self.max_batch_size:
            return Response({'error': f'Max batch size is {self.max_batch_size}'}, status=400)
        
        results = []
        for event in events:
            post_id = event.get('post_id')
            duration_ms = event.get('duration_ms')
            
            if not post_id or not duration_ms:
                continue
            
            engagement, _ = self.get_or_create_engagement(request.user, post_id)
            
            update_data = {
                'view_duration_ms': duration_ms,
                'scroll_depth': event.get('scroll_depth', 0),
                'visibility_ratio': event.get('visibility_ratio', 1.0)
            }
            
            weight = self.update_engagement_and_recalculate(engagement, **update_data)
            
            results.append({
                'post_id': post_id,
                'weight': round(weight, 4),
                'status': 'success'
            })
        
        return Response({
            'status': 'batch_processed',
            'processed_count': len(results),
            'results': results
        })


class FeedView(GenericAPIView):
    permission_classes = [IsAuthenticated]
       
    def get(self, request):
        
        limit = min(int(request.GET.get('limit', 20)), 50)
        offset = int(request.GET.get('offset', 0))
        
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        if not following_ids:
            return Response({'feed': [], 'count': 0})
        
        posts = Post.objects.filter(
            user_id__in=following_ids,
            is_deleted=False
        ).select_related('user__profile')
        
        scored_posts = []
        for post in posts:
            try:
                engagement = UserPostEngagement.objects.get(
                    user=request.user, post=post
                )
                weight = engagement.total_value_score
            except:
             
                comments_count = post.comments_count if hasattr(post, 'comments_count') else post.comments.count()
                popularity = likes_count + comments_count * 2
                weight = min(0.2 + (popularity / 1000), 0.5)
            
            scored_posts.append((weight, post))
        
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        paginated = scored_posts[offset:offset+limit]
        
        from apps.posts.serializers import PostSerializer
        serializer = PostSerializer([p for _, p in paginated], many=True, context={'request': request})
        
        return Response({
            'feed': serializer.data,
            'count': len(paginated),
            'has_more': len(paginated) == limit
        })



# class ExploreView(GenericAPIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
        
#         limit = min(int(request.GET.get('limit', 30)), 100)
#         offset = int(request.GET.get('offset', 0))
        
#         following_ids = Follow.objects.filter(
#             follower=request.user
#         ).values_list('following_id', flat=True)
        
#         week_ago = timezone.now() - timedelta(days=7) 
        
#         posts = Post.objects.filter(
#             created_at__gte=week_ago,
#             is_deleted=False
#         ).exclude(user_id__in=following_ids).exclude(user=request.user)
        
#         scored_posts = []
#         seen_users = set()
        
#         for post in posts:
#             if post.user_id in seen_users:
#                 continue
            
#             likes_count = post.likes_count if hasattr(post, 'likes_count') else post.likes.count()
#             comments_count = post.comments_count if hasattr(post, 'comments_count') else post.comments.count()
#             popularity = likes_count + comments_count * 2
#             popularity_score = min(popularity / 500, 0.5)
            
#             hours_old = (timezone.now() - post.created_at).total_seconds() / 3600 
#             recency_score = max(0, 1 - (hours_old / 168))
            
#             score = (popularity_score * 0.6) + (recency_score * 0.4)
#             scored_posts.append((score, post))
#             seen_users.add(post.user_id)
        
#         scored_posts.sort(key=lambda x: x[0], reverse=True)
#         paginated = scored_posts[offset:offset+limit]
        
#         from apps.posts.serializers import PostSerializer
#         serializer = PostSerializer([p for _, p in paginated], many=True, context={'request': request})
        
#         return Response({
#             'explore': serializer.data,
#             'count': len(paginated),
#             'has_more': len(paginated) == limit
#         })

# class ExploreView(GenericAPIView):
#     permission_classes = [IsAuthenticated]
    
#     def _is_ollama_available(self):
#         """بررسی در دسترس بودن Ollama"""
#         try:
#             from apps.ml.ollama_client import OllamaClient
#             client = OllamaClient()
#             result = client.generate("test", max_tokens=1, timeout=3)
#             return result.get('success', False)
#         except Exception as e:
#             return False
    
#     def _get_explore_with_ollama(self, request, limit, offset):
#         """اکسپلور با Ollama"""
#         from apps.interactions.services.explore_feed import ExploreFeedService
        
#         explore_service = ExploreFeedService(request.user)
#         result = explore_service.get_explore_feed(
#             limit=limit,
#             offset=offset,
#             use_ollama=True
#         )
#         return result
    
#     def get(self, request):
#         limit = min(int(request.GET.get('limit', 30)), 100)
#         offset = int(request.GET.get('offset', 0))
#         use_ollama = request.GET.get('use_ollama', 'true').lower() == 'true'
        
#         # اگر کاربر Ollama رو میخواد و در دسترسه
#         if use_ollama and self._is_ollama_available():
#             try:
#                 result = self._get_explore_with_ollama(request, limit, offset)
                
#                 if result.get('posts') and len(result['posts']) > 0:
#                     from apps.posts.serializers import PostSerializer
#                     serialized_posts = PostSerializer(
#                         result['posts'],
#                         many=True,
#                         context={'request': request}
#                     ).data
                    
#                     # اضافه کردن امتیاز و دلایل
#                     for i, post_data in enumerate(serialized_posts):
#                         if i < len(result.get('scores', [])):
#                             post_data['explore_score'] = result['scores'][i]
#                         if i < len(result.get('reasons', [])):
#                             post_data['explore_reasons'] = result['reasons'][i]
                    
#                     return Response({
#                         'explore': serialized_posts,
#                         'count': len(serialized_posts),
#                         'has_more': result.get('has_next', False),
#                         'used_hashtags': result.get('used_hashtags', []),
#                         'used_ollama': True,
#                         'algorithm': 'ollama'
#                     })
#             except Exception as e:
#                 pass  # میره سراغ fallback
        
#         # Fallback: الگوریتم ساده (کد قبلی خودت بدون تغییر)
#         following_ids = Follow.objects.filter(
#             follower=request.user
#         ).values_list('following_id', flat=True)
        
#         week_ago = timezone.now() - timedelta(days=7) 
        
#         posts = Post.objects.filter(
#             created_at__gte=week_ago,
#             is_deleted=False
#         ).exclude(user_id__in=following_ids).exclude(user=request.user)
        
#         scored_posts = []
#         seen_users = set()
        
#         for post in posts:
#             if post.user_id in seen_users:
#                 continue
            
#             likes_count = post.likes_count if hasattr(post, 'likes_count') else post.likes.count()
#             comments_count = post.comments_count if hasattr(post, 'comments_count') else post.comments.count()
#             popularity = likes_count + comments_count * 2
#             popularity_score = min(popularity / 500, 0.5)
            
#             hours_old = (timezone.now() - post.created_at).total_seconds() / 3600
#             recency_score = max(0, 1 - (hours_old / 168))
            
#             score = (popularity_score * 0.6) + (recency_score * 0.4)
#             scored_posts.append((score, post))
#             seen_users.add(post.user_id)
        
#         scored_posts.sort(key=lambda x: x[0], reverse=True)
#         paginated = scored_posts[offset:offset+limit]
        
#         from apps.posts.serializers import PostSerializer
#         serializer = PostSerializer([p for _, p in paginated], many=True, context={'request': request})
        
#         return Response({
#             'explore': serializer.data,
#             'count': len(paginated),
#             'has_more': len(paginated) == limit,
#             'used_ollama': False,
#             'algorithm': 'simple'
#         })






class ExploreView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def _is_ollama_available(self):
        """بررسی در دسترس بودن Ollama"""
        try:
            from apps.ml.ollama_client import OllamaClient
            client = OllamaClient()
            result = client.generate("test", max_tokens=1, timeout=3)
            return result.get('success', False)
        except Exception as e:
            return False
    
    def _get_explore_with_ollama(self, request, limit, offset):
        """اکسپلور با Ollama"""
        from apps.interactions.services.explore_feed import ExploreFeedService
        
        explore_service = ExploreFeedService(request.user)
        result = explore_service.get_explore_feed(
            limit=limit,
            offset=offset,
            use_ollama=True
        )
        return result
    
    def get(self, request):
        from django.db.models import Count
        
        limit = min(int(request.GET.get('limit', 30)), 100)
        offset = int(request.GET.get('offset', 0))
        use_ollama = request.GET.get('use_ollama', 'true').lower() == 'true'
        
        # اگر کاربر Ollama رو میخواد و در دسترسه
        if use_ollama and self._is_ollama_available():
            try:
                result = self._get_explore_with_ollama(request, limit, offset)
                
                if result.get('posts') and len(result['posts']) > 0:
                    from apps.posts.serializers import PostSerializer
                    serialized_posts = PostSerializer(
                        result['posts'],
                        many=True,
                        context={'request': request}
                    ).data
                    
                    # اضافه کردن امتیاز و دلایل
                    for i, post_data in enumerate(serialized_posts):
                        if i < len(result.get('scores', [])):
                            post_data['explore_score'] = result['scores'][i]
                        if i < len(result.get('reasons', [])):
                            post_data['explore_reasons'] = result['reasons'][i]
                    
                    return Response({
                        'explore': serialized_posts,
                        'count': len(serialized_posts),
                        'has_more': result.get('has_next', False),
                        'used_hashtags': result.get('used_hashtags', []),
                        'used_ollama': True,
                        'algorithm': 'ollama'
                    })
            except Exception as e:
                pass  # میره سراغ fallback
        
        # ✅ استفاده از annotate برای مرتب‌سازی بر اساس تعداد لایک
        posts = Post.objects.filter(
            is_deleted=False
        ).annotate(
            like_count=Count('likes')  # ایجاد فیلد مجازی like_count
        ).order_by('-like_count', '-created_at')  # مرتب‌سازی بر اساس like_count
        
        total_count = posts.count()
        paginated_posts = posts[offset:offset + limit]
        
        from apps.posts.serializers import PostSerializer
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return Response({
            'explore': serializer.data,
            'count': len(paginated_posts),
            'total_count': total_count,
            'has_more': (offset + limit) < total_count,
            'used_ollama': False,
            'algorithm': 'popularity_by_likes'
        })




class ComparePostView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        from apps.interactions.models import UserPostEngagement
        
        try:
            current = UserPostEngagement.objects.get(
                user=request.user, post_id=post_id
            )
            current_weight = current.total_value_score
        except:
            current_weight = 0.0
         
        recent = UserPostEngagement.objects.filter(
            user=request.user
        ).exclude(post_id=post_id).order_by('-updated_at')[:10]
        
        other_weights = [e.total_value_score for e in recent]
        all_weights = other_weights + [current_weight]
        all_weights.sort(reverse=True)
        rank = all_weights.index(current_weight) + 1
        
        comparisons = []
        for eng in recent:
            comparisons.append({
                'post_id': str(eng.post_id),
                'weight': round(eng.total_value_score, 4),
                'is_better': current_weight > eng.total_value_score
            })
        
        return Response({
            'post_id': post_id,
            'current_weight': round(current_weight, 4),
            'rank': rank,
            'total_compared': len(all_weights),
            'better_than': sum(1 for w in other_weights if w < current_weight),
            'comparisons': comparisons
        })


class PostStatsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        from apps.interactions.models import UserPostEngagement
        from apps.interactions.services.statistical_analyzer import StatisticalAnalyzer
        
        stats = StatisticalAnalyzer.analyze_post_engagement(post_id)
        
        try:
            user_engagement = UserPostEngagement.objects.get(
                user=request.user, post_id=post_id
            )
            user_data = {
                'view_duration_ms': user_engagement.view_duration_ms,
                'liked': user_engagement.liked_at is not None,
                'saved': user_engagement.saved_at is not None,
                'weight': round(user_engagement.total_value_score, 4)
            }
        except:
            user_data = None
        
        return Response({
            'post_id': post_id,
            'statistics': {
                'sample_size': stats.sample_size,
                'mean_view_ms': round(stats.mean, 2),
                'median_view_ms': round(stats.median, 2),
                'variance': round(stats.variance, 2),
                'std_dev': round(stats.std_dev, 2),
                'is_reliable': stats.is_reliable
            },
            'your_engagement': user_data
        })