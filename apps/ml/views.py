# apps/ml/views.py

import json
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.core.cache import cache
from .services.ollama_client import OllamaClient
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.core.cache import cache
from .serializers import (
    ExploreFeedQuerySerializer,
    RefreshExploreSerializer,
    HashtagRecommendationsQuerySerializer,
    PhoneNumberSerializer,
    BulkAnalysisSerializer,
    ContentModerationRequestSerializer,
    TrainModelRequestSerializer,
    ModelPredictionRequestSerializer,
    BatchPredictionRequestSerializer
)

User = get_user_model()


@method_decorator(staff_member_required, name='dispatch')
class AdminAnalyzeUserView(View):
    """
    Admin view for analyzing user data with AI
    """
    
    def get(self, request, user_id):
        try:
            # Find user
            try:
                user = User.objects.get(id=user_id)
            except (ValueError, User.DoesNotExist):
                try:
                    user = User.objects.get(id=int(user_id))
                except:
                    return JsonResponse({
                        'success': False,
                        'error': f'کاربر با آیدی {user_id} یافت نشد'
                    }, status=404)
            
            from apps.ml.services.file_analyzer import UserFilesAnalyzer
            
            files_analyzer = UserFilesAnalyzer(user)
            files_data = files_analyzer.analyze_all_files()
            
            profile_data = {
                'full_name': None,
                'bio': None,
                'avatar': None
            }
            try:
                if hasattr(user, 'profile') and user.profile:
                    profile_data['full_name'] = user.profile.full_name
                    profile_data['bio'] = user.profile.bio
                    if user.profile.avatar:
                        profile_data['avatar'] = user.profile.avatar.url
            except:
                pass

            posts_count = 0
            total_likes_received = 0
            posts_content = []
            posts_text = "پستی وجود ندارد"

            try:
                from apps.posts.models import Post
                posts = Post.objects.filter(user=user)
                posts_count = posts.count()
                total_likes_received = sum(p.likes.count() for p in posts)
                
                # Get content of text posts
                for post_item in posts:
                    if post_item.content:
                        posts_content.append(f"پست {post_item.id}: {post_item.content[:200]}")
                posts_text = "\n".join(posts_content[:5])
                
            except Exception as e:
                print(f"Error in posts: {e}")

            likes_given = 0
            try:
                from apps.posts.models import Like
                likes_given = Like.objects.filter(user=user).count()
            except:
                pass
            
            comments_count = 0
            try:
                from apps.posts.models import Comment
                comments_count = Comment.objects.filter(user=user).count()
            except:
                pass
            
            followers_count = 0
            following_count = 0
            try:
                from apps.follows.models import Follow
                followers_count = Follow.objects.filter(following=user).count()
                following_count = Follow.objects.filter(follower=user).count()
            except:
                pass
            
            top_hashtags = []
            try:
                from apps.hashtags.models import PostHashtag
                hashtags = PostHashtag.objects.filter(post__user=user).values('hashtag__name').annotate(
                    count=Count('id')).order_by('-count')[:5]
                top_hashtags = [
                    {'name': h['hashtag__name'], 'count': h['count']} 
                    for h in hashtags if h['hashtag__name']
                ]
            except:
                pass
            
            activity_score = (posts_count * 10) + (likes_given * 2) + (comments_count * 3)
            if activity_score > 100:
                activity_level = "high"
                activity_level_fa = "زیاد"
            elif activity_score > 50:
                activity_level = "medium"
                activity_level_fa = "متوسط"
            else:
                activity_level = "low"
                activity_level_fa = "کم"
            
            files_content_summary = ""
            if files_data.get('combined_content'):
                files_content_summary = f"""
            --- محتوای استخراج شده از فایل‌های کاربر ---
            {files_data['combined_content'][:1500]}

            انواع فایل‌ها: {', '.join([f"{k} ({v} فایل)" for k, v in files_data.get('file_types', {}).items()])}
            تعداد کل فایل‌ها: {files_data.get('total_files', 0)}
            --- پایان محتوای فایل‌ها ---
            """

            prompt = f"""شما یک روانشناس و تحلیلگر داده حرفه‌ای هستید. یک کاربر شبکه اجتماعی را بر اساس اطلاعات زیر تحلیل کنید:

            === اطلاعات کاربر ===
            شماره تلفن: {user.phone}
            نام کامل: {profile_data['full_name'] or 'ثبت نشده'}
            بیوگرافی: {profile_data['bio'] or 'ثبت نشده'}

            === محتوای پست‌های کاربر ===
            {posts_text}

            === آمار فعالیت در شبکه اجتماعی ===
            تعداد پست‌ها: {posts_count}
            تعداد لایک‌های داده شده: {likes_given}
            تعداد کامنت‌ها: {comments_count}
            تعداد دنبال‌کنندگان: {followers_count}
            تعداد دنبال‌شوندگان: {following_count}
            مجموع لایک‌های دریافتی: {total_likes_received}
            سطح فعالیت: {activity_level_fa}

            === هشتگ‌های پراستفاده ===
            {', '.join([f"#{h['name']}" for h in top_hashtags]) if top_hashtags else 'هیچ هشتگی ثبت نشده'}

            {files_content_summary}

            لطفاً یک تحلیل عمیق و حرفه‌ای به زبان فارسی انجام بده و نتیجه را دقیقاً به صورت JSON زیر برگردان (هیچ متن دیگری خارج از JSON ننویس):

            {{
                "personality_type": "نوع شخصیت کاربر",
                "personality_description": "توضیح کامل شخصیت کاربر در ۲-۳ جمله",
                "content_preferences": ["نوع محتوای مورد علاقه 1", "نوع محتوای مورد علاقه 2", "نوع محتوای مورد علاقه 3"],
                "strengths": ["نقطه قوت 1", "نقطه قوت 2", "نقطه قوت 3"],
                "weaknesses": ["نقطه ضعف 1", "نقطه ضعف 2"],
                "suggestions": ["پیشنهاد برای بهبود 1", "پیشنهاد برای بهبود 2", "پیشنهاد برای بهبود 3", "پیشنهاد برای بهبود 4"],
                "recommended_hashtags": ["هشتگ1", "هشتگ2", "هشتگ3", "هشتگ4", "هشتگ5"],
                "files_analysis_summary": "اگر فایلی وجود دارد، خلاصه‌ای از محتوای فایل‌ها و ارتباط آن با شخصیت کاربر. اگر فایلی نیست: 'کاربر فایلی برای تحلیل آپلود نکرده است'",
                "summary": "خلاصه نهایی و توصیه کلی در یک پاراگراف"
            }}

            فقط JSON را برگردان، هیچ متن اضافه‌ای قبل یا بعد از آن ننویس."""
            
            client = OllamaClient()
            client.model_name = "gemma3:27b"
            result = client.generate(prompt, temperature=0.7, max_tokens=2000)
            ai_analysis = {}
            if result.get('success'):
                try:
                    response_text = result.get('response', '')
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = response_text[start:end]
                        ai_analysis = json.loads(json_str)
                    else:
                        ai_analysis = {'raw_response': response_text}
                except json.JSONDecodeError as e:
                    ai_analysis = {
                        'raw_response': result.get('response', ''),
                        'parse_error': str(e)
                    }
            else:
                ai_analysis = {
                    'error': result.get('error', 'خطا در ارتباط با Ollama'),
                    'ollama_status': 'مشکل در اتصال'
                }

            return JsonResponse({
                'success': result.get('success', False),
                'user': {
                    'id': str(user.id),
                    'phone': user.phone,
                    'profile': profile_data,
                    'date_joined': user.date_joined.strftime('%Y/%m/%d') if user.date_joined else None
                },
                'statistics': {
                    'posts_count': posts_count,
                    'likes_given': likes_given,
                    'comments_count': comments_count,
                    'followers_count': followers_count,
                    'following_count': following_count,
                    'total_likes_received': total_likes_received,
                    'activity_level': activity_level_fa,
                    'activity_score': activity_score
                },
                'hashtags': top_hashtags,
                'files_summary': {
                    'total_files': files_data.get('total_files', 0),
                    'total_size_kb': files_data.get('total_size_bytes', 0) // 1024,
                    'file_types': files_data.get('file_types', {})
                },
                'ai_analysis': ai_analysis
            }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'error_type': e.__class__.__name__
            }, status=500)


class ExploreFeedView(GenericAPIView):
    """
    Get personalized explore feed with ML-powered recommendations
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExploreFeedQuerySerializer
    
    def get(self, request):
        query_serializer = self.get_serializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        limit = query_serializer.validated_data.get('limit', 20)
        offset = query_serializer.validated_data.get('offset', 0)
        use_ollama = query_serializer.validated_data.get('use_ollama', True)
        
        from .services.smart_feed_service import SmartFeedService
        from apps.posts.serializers import PostSerializer
        
        feed_service = SmartFeedService(request.user)
        feed_data = feed_service.get_smart_feed(
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
                "used_ollama": feed_data.get('used_ollama', False),
                "pagination": {
                    "total_count": feed_data['total_count'],
                    "has_next": feed_data['has_next'],
                    "limit": limit,
                    "offset": offset
                }
            }
        }, status=status.HTTP_200_OK)


class RefreshExploreView(GenericAPIView):
    """
    Refresh explore feed cache
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RefreshExploreSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cache.delete_pattern(f"smart_feed_{request.user.id}_*")
        
        from .services.ollama_hashtag_service import OllamaHashtagService
        
        ollama_service = OllamaHashtagService(request.user)
        hashtags = ollama_service.get_recommended_hashtags(force_refresh=True)
        
        return Response({
            "success": True,
            "message": "اکسپلور در حال بازسازی است",
            "hashtags": hashtags
        }, status=status.HTTP_200_OK)


class HashtagRecommendationsView(GenericAPIView):
    """
    Get AI-powered hashtag recommendations
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HashtagRecommendationsQuerySerializer
    
    def get(self, request):
        # Validate query parameters
        query_serializer = self.get_serializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        refresh = query_serializer.validated_data.get('refresh', False)
        
        from .services.ollama_hashtag_service import OllamaHashtagService
        
        ollama_service = OllamaHashtagService(request.user)
        hashtags = ollama_service.get_recommended_hashtags(force_refresh=refresh)
        
        return Response({
            "success": True,
            "data": {
                "hashtags": hashtags,
                "source": "ollama" if refresh else "cache",
                "count": len(hashtags)
            }
        }, status=status.HTTP_200_OK)


class ContentModerationView(GenericAPIView):
    """
    Moderate content using ML model
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentModerationRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .services.moderation_service import ContentModerationService
        
        moderation_service = ContentModerationService()
        result = moderation_service.moderate(
            content=serializer.validated_data['content'],
            content_type=serializer.validated_data['type'],
            language=serializer.validated_data.get('language', 'fa')
        )
        
        return Response({
            "success": True,
            "data": result
        }, status=status.HTTP_200_OK)


class TrainModelView(GenericAPIView):
    """
    Train ML models (admin only)
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = TrainModelRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .services.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        result = trainer.train_models(
            model_type=serializer.validated_data['model_type'],
            force_retrain=serializer.validated_data['force_retrain'],
            use_gpu=serializer.validated_data['use_gpu'],
            validation_split=serializer.validated_data['validation_split']
        )
        
        return Response({
            "success": True,
            "message": "مدل با موفقیت آموزش داده شد",
            "result": result
        }, status=status.HTTP_200_OK)


class ModelHealthView(GenericAPIView):
    """
    Check health status of all ML models
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        from .services.model_registry import ModelRegistry
        
        registry = ModelRegistry()
        models_status = registry.get_all_models_status()
        
        return Response({
            "success": True,
            "data": {
                "models": models_status,
                "total_models": len(models_status)
            }
        }, status=status.HTTP_200_OK)


class ModelPredictionView(GenericAPIView):
    """
    Make predictions using ML models
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ModelPredictionRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .services.prediction_service import PredictionService
        
        prediction_service = PredictionService()
        result = prediction_service.predict(
            model_type=serializer.validated_data['model_type'],
            input_data=serializer.validated_data['input_data'],
            use_cache=serializer.validated_data['use_cache']
        )
        
        return Response({
            "success": True,
            "data": result
        }, status=status.HTTP_200_OK)


class BatchPredictionView(GenericAPIView):
    """
    Make batch predictions using ML models
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BatchPredictionRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .services.prediction_service import PredictionService
        
        prediction_service = PredictionService()
        results = prediction_service.batch_predict(
            model_type=serializer.validated_data['model_type'],
            inputs=serializer.validated_data['inputs'],
            use_cache=serializer.validated_data['use_cache']
        )
        
        return Response({
            "success": True,
            "data": results
        }, status=status.HTTP_200_OK)