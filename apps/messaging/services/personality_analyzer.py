# apps/messaging/services/personality_analyzer.py

import logging
import json
import re
from collections import Counter
from django.db.models import Count
from django.core.cache import cache
from django.conf import settings

from apps.posts.models import Post, Like, Comment
from apps.hashtags.models import PostHashtag
from apps.follows.models import Follow

logger = logging.getLogger(__name__)


class OllamaClient:
    """کلاینت اتصال به Ollama"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'gemma3:27b')
        self.enabled = getattr(settings, 'OLLAMA_ENABLED', False)  # 🟢 پیش‌فرض False
    
    def is_available(self):
        """بررسی در دسترس بودن Ollama"""
        if not self.enabled:
            return False
        
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt, temperature=0.7, max_tokens=500):
        """ارسال درخواست به Ollama"""
        if not self.is_available():
            return {"success": False, "error": "Ollama در دسترس نیست"}
        
        import requests
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json().get("response", "")
                }
            return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class TargetPersonalityAnalyzer:
    """
    تحلیل شخصیت فرد مقابل (قابلیت مخ زنی)
    """
    
    def __init__(self, target_user):
        self.target = target_user
        self._ollama_client = None
    
    def _get_ollama_client(self):
        if self._ollama_client is None:
            self._ollama_client = OllamaClient()
        return self._ollama_client
    
    def analyze_target(self, force_refresh=False):
        """تحلیل کامل فرد مقابل"""
        cache_key = f"target_analysis_{self.target.id}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        data = self._collect_data()
        
        # 🟢 اگر Ollama فعال باشد، از AI استفاده کن
        ollama = self._get_ollama_client()
        if ollama.is_available():
            analysis = self._ai_analysis(data)
        else:
            analysis = self._static_analysis(data)  # پاسخ استاتیک
        
        cache.set(cache_key, analysis, 60 * 60 * 6)
        return analysis
    
    def _collect_data(self):
        """جمع‌آوری داده‌های کاربر"""
        posts = Post.objects.filter(user=self.target, is_deleted=False)
        
        hashtags = PostHashtag.objects.filter(
            post__user=self.target
        ).values('hashtag__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        liked_posts = Like.objects.filter(user=self.target).values_list('post_id', flat=True)[:50]
        liked_hashtags = PostHashtag.objects.filter(
            post_id__in=liked_posts
        ).values_list('hashtag__name', flat=True)
        
        bio = ""
        if hasattr(self.target, 'profile') and self.target.profile:
            bio = self.target.profile.bio or ""
        
        followers_count = Follow.objects.filter(following=self.target).count()
        following_count = Follow.objects.filter(follower=self.target).count()
        
        return {
            "username": self.target.username,
            "bio": bio,
            "posts_count": posts.count(),
            "followers_count": followers_count,
            "following_count": following_count,
            "top_hashtags": [h['hashtag__name'] for h in hashtags],
            "liked_hashtags": list(set(liked_hashtags))[:10],
        }
    
    def _ai_analysis(self, data):
        """تحلیل با Ollama (هوشمند)"""
        ollama = self._get_ollama_client()
        
        prompt = f"""
        شما یک مشاور روابط اجتماعی هستید. بر اساس اطلاعات زیر، شخصیت فرد را تحلیل کن:
        
        اطلاعات فرد:
        - نام کاربری: {data.get('username')}
        - بیوگرافی: {data.get('bio', 'ندارد')}
        - تعداد پست: {data.get('posts_count', 0)}
        - تعداد فالوور: {data.get('followers_count', 0)}
        - هشتگ‌های پرکاربرد: {data.get('top_hashtags', [])[:5]}
        
        خروجی JSON:
        {{
            "personality_type": "نوع شخصیت",
            "interests": ["علاقه1", "علاقه2", "علاقه3"],
            "communication_style": "سبک ارتباطی",
            "icebreakers": ["موضوع1", "موضوع2"],
            "topics_to_avoid": ["موضوع1"],
            "best_time_to_message": "زمان پیشنهادی",
            "tips": ["نکته1", "نکته2"]
        }}
        """
        
        try:
            result = ollama.generate(prompt, temperature=0.7, max_tokens=600)
            if result.get('success'):
                text = result.get('response', '')
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
        
        return self._static_analysis(data)
    
    def _static_analysis(self, data):
        """تحلیل استاتیک (بدون AI) - همیشه کار می‌کند"""
        interests = data.get('top_hashtags', [])[:3]
        
        return {
            "personality_type": "برون‌گرا" if data.get('posts_count', 0) > 20 else "درون‌گرا",
            "interests": interests if interests else ["هنر", "موسیقی", "سفر"],
            "communication_style": "صمیمی و دوستانه",
            "icebreakers": [f"درباره {interests[0]}" if interests else "درباره علایق مشترک"],
            "topics_to_avoid": ["مسائل شخصی خیلی خصوصی"],
            "best_time_to_message": "عصرها",
            "tips": ["با سلام دوستانه شروع کن", "به پست‌هایش واکنش نشان بده"]
        }


class MessageSuggestionService:
    """
    سرویس پیشنهاد پیام (مخ زنی)
    """
    
    def __init__(self, user, target_user):
        self.user = user
        self.target = target_user
        self.analyzer = TargetPersonalityAnalyzer(target_user)
    
    def get_opening_message_suggestions(self, count=3):
        """پیشنهاد پیام‌های شروع کننده"""
        
        analysis = self.analyzer.analyze_target()
        ollama = self.analyzer._get_ollama_client()
        
        # 🟢 اگر Ollama فعال باشد، پیام‌های هوشمند بده
        if ollama.is_available():
            return self._ai_message_suggestions(analysis, count)
        
        return self._static_message_suggestions(analysis, count)
    
    def _ai_message_suggestions(self, analysis, count):
        """پیشنهاد پیام با AI"""
        ollama = self.analyzer._get_ollama_client()
        
        prompt = f"""
        اطلاعات فرد مقابل:
        - تیپ شخصیتی: {analysis.get('personality_type')}
        - علایق: {analysis.get('interests', [])}
        
        {count} پیام کوتاه و صمیمی برای شروع مکالمه پیشنهاد بده.
        فقط لیست JSON برگردان. مثال: ["پیام1", "پیام2"]
        """
        
        try:
            result = ollama.generate(prompt, temperature=0.8, max_tokens=200)
            if result.get('success'):
                text = result.get('response', '')
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    return json.loads(match.group())[:count]
        except Exception as e:
            logger.error(f"AI message error: {e}")
        
        return self._static_message_suggestions(analysis, count)
    
    def _static_message_suggestions(self, analysis, count):
        """پیشنهاد پیام استاتیک (بدون AI)"""
        interests = analysis.get('interests', [])
        
        suggestions = [
            "سلام! حال دیدن پست‌هات خوب بود 👋",
            "سلام چطوری؟ پروفایل جالبی داری 😊",
            "چه روز خوبی! امیدوارم روزت عالی باشه ✨",
        ]
        
        if interests:
            suggestions.append(f"سلام! دیدم به {interests[0]} علاقه داری، منم خیلی دوست دارم 🤝")
        
        return suggestions[:count]
    
    def get_reply_suggestion(self, last_message):
        """پیشنهاد پاسخ به آخرین پیام"""
        
        ollama = self.analyzer._get_ollama_client()
        
        if ollama.is_available():
            prompt = f"""
            آخرین پیام دریافتی: "{last_message}"
            یک پاسخ طبیعی، دوستانه و کوتاه پیشنهاد بده.
            فقط متن پاسخ را برگردان.
            """
            try:
                result = ollama.generate(prompt, temperature=0.8, max_tokens=100)
                if result.get('success'):
                    return result.get('response', '')
            except:
                pass
        
        # پاسخ استاتیک
        static_replies = [
            "چه جالب! بگو بیشتر برام 😊",
            "آره دقیقاً! منم همینطور فکر می‌کنم 🤝",
            "وای چه خوب! برام جالبه 🎯",
            "چیز جالبی گفتی! ادامه بده 👀"
        ]
        return static_replies[0]
