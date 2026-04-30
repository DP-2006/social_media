
# apps/accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.services.sms_service import OTPService
from .models import OTP, User

User = get_user_model()

class RegisterSendOTPView(APIView):
    permission_classes = [ AllowAny ]
    
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'success': False, 'error': 'the phoen number is must be enter it !!thanks for attention this matter'}, status=400)
        
        success, message = OTPService.send_otp( phone )
        #this fields for sample mode mot use the opperations when run the systems for when user cant get the code and then user use the last otp code resived 
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
        }, status=200 if success else 400)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if not phone or not code:
            return Response({'success': False, 'error': 'the code and phone number muste be enter it ! '}, status=400)
        
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
        
        return Response({'success': False, 'error': message}, status=400)
# for deffens the  DOS
class LoginSendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'success': False, 'error': 'ples ENTER YOUR PHONE !'}, status=400)
        
        from core.services.sms_service import OTPService as OTPServiceClass
        normalized_phone = OTPServiceClass.normalize_phone(phone)
        
        try:
            user = User.objects.get(phone=normalized_phone)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'not found any user and mobile number her '}, status=404)
        
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
        }, status=200 if success else 400)

#this for possition of user or users   when logging in pass (like logging in 2 days ago the user is loggined  )
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'success': True, 'message': 'succses exit'})
        except Exception:
            return Response({'success': True, 'message': 'exit'})