# # core/services/sms_service.py

# from abc import ABC, abstractmethod
# import random
# import logging
# from datetime import datetime, timedelta

# logger = logging.getLogger(__name__)


# class SMSProvider(ABC):
    
#     @abstractmethod
#     def send(self, phone: str, code: str) -> bool:
#         pass


# class KavenegarSMS(SMSProvider):
    
#     def __init__(self, api_key: str = None, sender: str = None):
#         from django.conf import settings
#         self.api_key = api_key or getattr(settings, 'KAVENEGAR_API_KEY', '')
#         self.sender = sender or getattr(settings, 'SMS_SENDER', '')
    
#     def send(self, phone: str, code: str) -> bool:
#         try:
#             from kavenegar import KavenegarAPI
            
#             api = KavenegarAPI(self.api_key)
#             params = {
#                 'sender': self.sender,
#                 'receptor': phone,
#                 'message': f'کد تأیید شما: {code}'
#             }
            
#             response = api.sms_send(params)
#             logger.info(f"SMS sent to {phone}: {response}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send SMS: {e}")
#             return False


# class GhasedakSMS(SMSProvider):
    
#     def __init__(self, api_key: str = None, line_number: str = None):
#         from django.conf import settings
#         self.api_key = api_key or getattr(settings, 'GHASEDAK_API_KEY', '')
#         self.line_number = line_number or getattr(settings, 'SMS_LINE_NUMBER', '')
    
#     def send(self, phone: str, code: str) -> bool:
#         try:
#             from ghasedak import Ghasedak # type: ignore
            
#             sms = Ghasedak(self.api_key)
#             response = sms.send_simple({
#                 'message': f'کد تأیید شما: {code}',
#                 'line_number': self.line_number,
#                 'receptor': phone
#             })
            
#             logger.info(f"SMS sent to {phone}: {response}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send SMS: {e}")
#             return False


# class FakeSMSProvider(SMSProvider):
    
#     def send(self, phone: str, code: str) -> bool:
#         logger.info(f"📱 [FAKE SMS] To: {phone} | Code: {code}")
#         return True


# def get_sms_provider() -> SMSProvider:
#     from django.conf import settings
#     import sys
    
#     provider = getattr(settings, 'SMS_PROVIDER', 'fake')
    
#     if 'test' in sys.argv or 'check' in sys.argv:
#         return FakeSMSProvider()
    
#     providers = {
#         'kavenegar': KavenegarSMS,
#         'ghasedak': GhasedakSMS,
#         'fake': FakeSMSProvider,
#     }
    
#     return providers.get(provider, FakeSMSProvider)()


# class OTPService:
    
#     CODE_LENGTH = 6
#     EXPIRY_MINUTES = 5
#     MAX_ATTEMPTS = 3
    
#     @staticmethod
#     def generate_code() -> str:
#         return ''.join(random.choices('0123456789', k=OTPService.CODE_LENGTH))
    
#     @staticmethod
#     def send_otp(phone: str) -> tuple:
#         from apps.accounts.models import OTP
        
#         recent_count = OTP.objects.filter(
#             phone=phone,
#             created_at__gte=datetime.now() - timedelta(minutes=1)
#         ).count()
        
#         if recent_count >= 3:
#             return False, "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً یک دقیقه صبر کنید."
        
#         code = OTPService.generate_code()
        
#         OTP.objects.create(
#             phone=phone,
#             code=code,
#             expires_at=datetime.now() + timedelta(minutes=OTPService.EXPIRY_MINUTES)
#         )
        
#         provider = get_sms_provider()
#         if provider.send(phone, code):
#             return True, "کد تأیید ارسال شد"
        
#         return False, "خطا در ارسال پیامک"
    
#     @staticmethod
#     def verify_otp(phone: str, code: str) -> tuple:
#         """
#         بررسی کد OTP
#         Returns: (valid: bool, message: str)
#         """
#         from apps.accounts.models import OTP
#         from django.utils import timezone
        
#         try:
#             otp = OTP.objects.filter(
#                 phone=phone,
#                 is_used=False
#             ).latest('-created_at')
#         except OTP.DoesNotExist:
#             return False, "کد تأیید یافت نشد"
        
#         if otp.is_expired:
#             return False, "کد تأیید منقضی شده است"
        
#         otp.attempts += 1
#         if otp.attempts > OTPService.MAX_ATTEMPTS:
#             return False, "تعداد تلاش‌ها بیش از حد مجاز است"
        
#         if otp.code != code:
#             otp.save()
#             remaining = OTPService.MAX_ATTEMPTS - otp.attempts
#             return False, f"کد تأیید اشتباه است. {remaining} تلاش باقیمانده"
        
#         otp.is_used = True
#         otp.save()
        
#         return True, "کد تأیید صحیح است"

























# # core/services/sms_service.py

# from abc import ABC, abstractmethod
# import random
# import logging
# from datetime import datetime, timedelta

# logger = logging.getLogger(__name__)


# class SMSProvider(ABC):
    
#     @abstractmethod
#     def send(self, phone: str, code: str) -> bool:
#         pass


# class KavenegarSMS(SMSProvider):
#     """سرویس پیامک کاوه نگار"""
    
#     def __init__(self, api_key: str = None, sender: str = None):
#         from django.conf import settings
#         self.api_key = api_key or getattr(settings, 'KAVENEGAR_API_KEY', '4D706439326650596F41677543517261356B6A614142663053775846754D764D41474F424C69386E586D6B3D')
#         self.sender = sender or getattr(settings, 'SMS_SENDER', '2000660110')
    
#     def send(self, phone: str, code: str) -> bool:
#         try:
#             from kavenegar import KavenegarAPI
            
#             api = KavenegarAPI(self.api_key)
#             params = {
#                 'sender': self.sender,
#                 'receptor': phone,
#                 'message': f'کد تأیید شما: {code}'
#             }
            
#             response = api.sms_send(params)
#             logger.info(f"SMS sent to {phone}: {response}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send SMS: {e}")
#             return False


# class GhasedakSMS(SMSProvider):
#     """سرویس پیامک قاصدک"""
    
#     def __init__(self, api_key: str = None, line_number: str = None):
#         from django.conf import settings
#         self.api_key = api_key or getattr(settings, 'GHASEDAK_API_KEY', '')
#         self.line_number = line_number or getattr(settings, 'SMS_LINE_NUMBER', '')
    
#     def send(self, phone: str, code: str) -> bool:
#         try:
#             from ghasedak import Ghasedak
            
#             sms = Ghasedak(self.api_key)
#             response = sms.send_simple({
#                 'message': f'کد تأیید شما: {code}',
#                 'line_number': self.line_number,
#                 'receptor': phone
#             })
            
#             logger.info(f"SMS sent to {phone}: {response}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send SMS: {e}")
#             return False


# class FakeSMSProvider(SMSProvider):
#     """سرویس تستی - فقط در محیط توسعه"""
    
#     def send(self, phone: str, code: str) -> bool:
#         logger.info(f"📱 [FAKE SMS] To: {phone} | Code: {code}")
#         return True


# def get_sms_provider() -> SMSProvider:
#     """دریافت سرویس SMS بر اساس تنظیمات"""
#     from django.conf import settings
#     import sys
    
#     provider = getattr(settings, 'SMS_PROVIDER', 'fake')
    
#     if 'test' in sys.argv or 'check' in sys.argv:
#         return FakeSMSProvider()
    
#     providers = {
#         'kavenegar': KavenegarSMS,
#         'ghasedak': GhasedakSMS,
#         'fake': FakeSMSProvider,
#     }
    
#     provider_class = providers.get(provider, FakeSMSProvider)
#     return provider_class()


# class OTPService:
#     """سرویس مدیریت OTP"""
    
#     CODE_LENGTH = 6
#     EXPIRY_MINUTES = 5
#     MAX_ATTEMPTS = 3
    
#     @staticmethod
#     def generate_code() -> str:
#         """تولید کد تصادفی"""
#         return ''.join(random.choices('0123456789', k=OTPService.CODE_LENGTH))
    
#     @staticmethod
#     def send_otp(phone: str) -> tuple:
#         """
#         ارسال OTP به شماره موبایل
#         Returns: (success: bool, message: str)
#         """
#         from apps.accounts.models import OTP
        
#         # بررسی تعداد درخواست‌های اخیر
#         recent_count = OTP.objects.filter(
#             phone=phone,
#             created_at__gte=datetime.now() - timedelta(minutes=1)
#         ).count()
        
#         if recent_count >= 3:
#             return False, "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً یک دقیقه صبر کنید."
        
#         # تولید کد
#         code = OTPService.generate_code()
        
#         # ذخیره در دیتابیس
#         OTP.objects.create(
#             phone=phone,
#             code=code,
#             expires_at=datetime.now() + timedelta(minutes=OTPService.EXPIRY_MINUTES)
#         )
        
#         # ارسال پیامک
#         provider = get_sms_provider()
#         if provider.send(phone, code):
#             return True, "کد تأیید ارسال شد"
        
#         return False, "خطا در ارسال پیامک"
    
#     @staticmethod
#     def verify_otp(phone: str, code: str) -> tuple:
#         """
#         بررسی کد OTP
#         Returns: (valid: bool, message: str)
#         """
#         from apps.accounts.models import OTP
        
#         # دریافت آخرین کد
#         try:
#             otp = OTP.objects.filter(
#                 phone=phone,
#                 is_used=False
#             ).latest('-created_at')
#         except OTP.DoesNotExist:
#             return False, "کد تأیید یافت نشد"
        
#         # بررسی انقضا
#         if otp.is_expired:
#             return False, "کد تأیید منقضی شده است"
        
#         # بررسی تعداد تلاش
#         otp.attempts += 1
#         if otp.attempts > OTPService.MAX_ATTEMPTS:
#             otp.save()
#             return False, "تعداد تلاش‌ها بیش از حد مجاز است"
        
#         # بررسی کد
#         if otp.code != code:
#             otp.save()
#             remaining = OTPService.MAX_ATTEMPTS - otp.attempts
#             return False, f"کد تأیید اشتباه است. {remaining} تلاش باقیمانده"
        
#         # کد معتبر است
#         otp.is_used = True
#         otp.save()
        
#         return True, "کد تأیید صحیح است"




















# core/services/sms_service.py - کپی کامل و جایگزین کن

from abc import ABC, abstractmethod
import random
import re
import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class SMSProvider(ABC):
    
    @abstractmethod
    def send(self, phone: str, code: str) -> bool:
        pass


class KavenegarSMS(SMSProvider):
    def __init__(self, api_key: str = None, sender: str = None):
        from django.conf import settings
        self.api_key = api_key or getattr(settings, 'KAVENEGAR_API_KEY', '4D706439326650596F41677543517261356B6A614142663053775846754D764D41474F424C69386E586D6B3D')
        self.sender = sender or getattr(settings, 'SMS_SENDER', '2000660110')
    
    def send(self, phone: str, code: str) -> bool:
        try:
            from kavenegar import KavenegarAPI
            
            api = KavenegarAPI(self.api_key)
            params = {
                'sender': self.sender,
                'receptor': phone,
                'message': f'کد تأیید شما: {code}'
            }
            
            response = api.sms_send(params)
            logger.info(f"SMS sent to {phone}: {response}")
            print(f"SMS sent to {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            print(f" خطا در ارسال SMS: {e}")
            return False


class FakeSMSProvider(SMSProvider):
    
    def send(self, phone: str, code: str) -> bool:
        print(f" [FAKE SMS] To: {phone} | Code: {code}")
        return True


def get_sms_provider():
    from django.conf import settings
    import sys
    
    provider = getattr(settings, 'SMS_PROVIDER', 'kavenegar')
    
    if 'test' in sys.argv or 'check' in sys.argv:
        return FakeSMSProvider()
    
    providers = {
        'kavenegar': KavenegarSMS,
        'fake': FakeSMSProvider,
    }
    
    provider_class = providers.get(provider, FakeSMSProvider)
    return provider_class()


class OTPService:
    CODE_LENGTH = 6
    EXPIRY_MINUTES = 5 
    MAX_ATTEMPTS = 3
    
    @staticmethod
    def normalize_phone(phone):
        if not phone:
            return None
        cleaned = re.sub(r'\D', '', str(phone))
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        if not cleaned.startswith('98') and len(cleaned) == 10:
            cleaned = '98' + cleaned
        return cleaned
    
    @staticmethod
    def generate_code() -> str:
        return ''.join(random.choices('0123456789', k=OTPService.CODE_LENGTH))
    
    @staticmethod
    def send_otp(phone: str) -> tuple:
        from apps.accounts.models import OTP
        
        # نرمالایز شماره
        phone = OTPService.normalize_phone(phone)
        if not phone:
            return False, "شماره تلفن معتبر نیست"
        
        print(f" Send OTP to normalized phone: {phone}")
        
        # بررسی ریت لیمیت
        recent_count = OTP.objects.filter(
            phone=phone,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).count()
        
        if recent_count >= 3:
            return False, "تعداد درخواست‌های شما بیش از حد مجاز است"
        
        # غیرفعال کردن OTPهای قبلی استفاده نشده
        OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
        
        # تولید کد جدید
        code = OTPService.generate_code()
        expires_at = timezone.now() + timedelta(minutes=OTPService.EXPIRY_MINUTES)
        
        # ذخیره در دیتابیس
        otp = OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at,
            is_used=False
        )
        
        print(f" OTP created: phone={phone}, code={code}, expires_at={expires_at}")
        
        # ارسال SMS
        provider = get_sms_provider()
        if provider.send(phone, code):
            return True, "کد تأیید ارسال شد"
        
        return False, "خطا در ارسال پیامک"
    
    @staticmethod
    def verify_otp(phone: str, code: str) -> tuple:
        from apps.accounts.models import OTP
        
        # نرمالایز شماره
        phone = OTPService.normalize_phone(phone)
        if not phone:
            return False, "شماره تلفن معتبر نیست"
        
        print(f" Verify OTP: phone={phone}, code={code}")
        print(f" Current time: {timezone.now()}")
        
        # جستجوی OTP معتبر (استفاده نشده و منقضی نشده)
        try:
            otp = OTP.objects.get(
                phone=phone,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()  # ← این خط خیلی مهمه
            )
            print(f" OTP found valid: {otp.code}, expires_at={otp.expires_at}")
            
        except OTP.DoesNotExist:
            # لاگ دیباگ برای پیدا کردن مشکل
            all_otps = OTP.objects.filter(phone=phone, code=code)
            if all_otps.exists():
                for o in all_otps:
                    print(f" Found but invalid: code={o.code}, is_used={o.is_used}, expired={o.expires_at < timezone.now()}, expires_at={o.expires_at}")
            else:
                print(f" No OTP found with phone={phone} and code={code}")
            return False, "کد تأیید اشتباه یا منقضی شده است"
        
        # علامت‌گذاری به عنوان استفاده شده
        otp.is_used = True
        otp.save()
        
        print(f" OTP verified successfully for {phone}")
        return True, "کد تأیید صحیح است"