
# apps/accounts/serializers.py
import random
import re
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP


def normalize_phone(phone):
    if not phone:
        return None
    phone = str(phone)
    cleaned = re.sub(r'\D', '', phone)
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]
    if not cleaned.startswith('98') and len(cleaned) == 10:
        cleaned = '98' + cleaned
    return cleaned


class RegisterSerializer(serializers.Serializer):
    
    phone = serializers.CharField(max_length=20, min_length=10)
    
    def validate_phone(self, value):
        value = normalize_phone(value)
        
        if not value:
            raise serializers.ValidationError("phone number isnt valid ")
        
        if not value.isdigit():
            raise serializers.ValidationError("phone number have the numbers carecter plese write the correct forms ")
        
        return value
    
    def create_otp(self, phone):
        OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
        
        code = str(random.randint(100000, 999999))
        
        otp = OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        print(f" OTP for {phone}: {code}")
        return otp
    
    def save(self):
        return self.create_otp(self.validated_data['phone'])


class VerifyOTPSerializer(serializers.Serializer):
    
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')
        
        phone = normalize_phone(phone)
        
        if not phone:
            raise serializers.ValidationError({"phone": "the phone number is not valid "})
        
        print(f" Searching for phone: {phone}, code: {code}")
        
        try:
            otp = OTP.objects.get(phone=phone, code=code, is_used=False)
            print(f" OTP found: {otp.code}, expires_at: {otp.expires_at}")
        except OTP.DoesNotExist:
            latest = OTP.objects.filter(phone=phone).first()
            if latest:
                print(f" Last OTP for {phone}: code={latest.code}, is_used={latest.is_used}, expired={latest.expires_at < timezone.now()}")
            else:
                print(f" No OTP found for {phone}")
            raise serializers.ValidationError({"code":" the code is false or expier it "})
        
        if otp.expires_at < timezone.now():
            print(f" OTP expired: {otp.expires_at} < {timezone.now()}")
            raise serializers.ValidationError({"code": "the code has been expier it "})
        
        attrs['otp'] = otp
        attrs['phone'] = phone
        return attrs
    
    def save(self):
        otp = self.validated_data['otp']
        phone = self.validated_data['phone']
        
        otp.is_used = True
        otp.save()
        
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'username': f"user_{phone[-8:]}",
                'phone': phone
            }
        )
        
        return user, created


class LoginSerializer(serializers.Serializer):
    
    phone = serializers.CharField(max_length=20)
    
    def validate_phone(self, value):
        value = normalize_phone(value)
        
        if not value:
            raise serializers.ValidationError("the phone number is not valid ")
        
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("not found any user has this phonenumber ")
        
        return value
    
    def save(self):
        phone = self.validated_data['phone']
        
        OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
        
        code = str(random.randint(100000, 999999))
        
        otp = OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        print(f" Login OTP for {phone}: {code}")
        return otp