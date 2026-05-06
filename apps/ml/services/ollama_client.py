




import requests
import json
from django.conf import settings
from django.core.cache import cache

class OllamaClient:
    
    # FIX THIS LINE - remove hardcoded default
    def __init__(self, model_name=None):  # Changed from model_name='qwen:7b'
        # Read from settings, fallback to gemma3:27b
        self.model_name = model_name or getattr(settings, 'OLLAMA_MODEL', 'gemma3:27b')
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    
    def generate(self, prompt, temperature=0.7, max_tokens=2000):
        cache_key = f"ollama_{hash(prompt)}_{temperature}"
        
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens  
                    }
                },
                timeout=1500
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get('response', '')
                
                cache.set(cache_key, output, 180)
                
                return {
                    'success': True,
                    'response': output,
                    'tokens_used': result.get('eval_count', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Ollama در حال اجرا نیست. لطفاً 'ollama serve' را اجرا کنید."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat(self, messages, temperature=0.7):
        """چت با حفظ تاریخچه"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    'model': self.model_name,
                    'messages': messages,
                    'stream': False,
                    'options': {'temperature': temperature}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result.get('message', {}).get('content', '')
                }
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_personality_with_ai(self, user_data):
        
        prompt = f"""
        شما یک روانشناس متخصص هستید. بر اساس اطلاعات زیر، یک تحلیل شخصیت کامل ارائه دهید:
        
        اطلاعات کاربر:
        - بیوگرافی: {user_data.get('bio', 'ندارد')}
        - نمونه پست‌ها: {user_data.get('sample_posts', 'ندارد')[:500]}
        - هشتگ‌های پرکاربرد: {user_data.get('top_hashtags', [])}
        - تعداد پست: {user_data.get('posts_count', 0)}
        - تعداد فالوور: {user_data.get('followers_count', 0)}
        
        لطفاً خروجی را به صورت JSON با این ساختار برگردان:
        {{
            "personality_type": "نوع شخصیت",
            "core_values": ["ارزش1", "ارزش2", "ارزش3"],
            "psychological_analysis": "تحلیل روانشناختی",
            "recommendations": ["توصیه1", "توصیه2"]
        }}
        """
        
        result = self.generate(prompt, temperature=0.5)
        return result






    def check_health(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                return {
                    'status': 'healthy',
                    'models': models,
                    'model_available': self.model_name in models,
                    'message': f"✅ سرویس سالم است. مدل {self.model_name} {'موجود' if self.model_name in models else 'موجود نیست'}"
                }
            return {
                'status': 'unhealthy',
                'error': f"HTTP {response.status_code}"
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'error': 'connection_error',
                'message': '❌ به سرور Ollama متصل نمی‌شوم. لطفاً دستور "ollama serve" را اجرا کنید.'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
