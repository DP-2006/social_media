# apps/accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.services.sms_service import OTPService
from .models import OTP, User
from .serializers import (
    PhoneSerializer, 
    VerifyOTPSerializer, 
    LogoutSerializer
)
#یه جیز بگم اینجا ما یه بخش لاگین داریم یه verify داریم 
#یکی برای این حالت که طرف بار اولشه وارد سیستم شده لاگین میشه   و نمی تونه verify بشه 
#این بخش بزودی اضافه کنم که اگر طرف نتونست کد otp رو بگیره با آخرین کدی که ارسال شده و منقضی نشده  وارد بشه 
User = get_user_model()
class RegisterSendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        
        success, message = OTPService.send_otp(phone)
        
        code_for_test = None
        if success:
            try:
                otp = OTP.objects.filter(phone=phone, is_used=False).latest('created_at')
                code_for_test = otp.code  
                print(f"test code tests: {code_for_test}")
            except:
                pass

        return Response({
            'success': success,
            'message': message,
            'code_for_test': code_for_test
        }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        
        success, message = OTPService.verify_otp(phone, code)
        
        if success:
            from core.services.sms_service import OTPService as OTPServiceClass
            normalized_phone = OTPServiceClass.normalize_phone(phone)
            
            user, created = User.objects.get_or_create(
                phone=normalized_phone,
                defaults={'username': f"user_{normalized_phone[-8:]}"}
            )
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'sucssesfully regester' if created else 'sucssesfully enter',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user_id': str(user.id),
                'is_new': created
            })
        
        return Response({'success': False, 'error': message}, status=status.HTTP_400_BAD_REQUEST)


class LoginSendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        
        from core.services.sms_service import OTPService as OTPServiceClass
        normalized_phone = OTPServiceClass.normalize_phone(phone)
        
        try:
            user = User.objects.get(phone=normalized_phone)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'not found any user and mobile number her '}, status=status.HTTP_404_NOT_FOUND)
        
        success, message = OTPService.send_otp(phone)
        
        code_for_test = None
        if success:
            try:
                otp = OTP.objects.filter(phone=normalized_phone, is_used=False).latest('created_at')
                code_for_test = otp.code
            except:
                pass
        
        return Response({
            'success': success,
            'message': message,
            'code_for_test': code_for_test
        }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh_token = serializer.validated_data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'success': True, 'message': 'succses exit'})
        except Exception:
            return Response({'success': True, 'message': 'exit'})