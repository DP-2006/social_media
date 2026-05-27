# apps/accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
import random
import string


class UserManager(BaseUserManager):
    
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره تلفن الزامی است')
        phone = self.normalize_phone(phone)
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)
    
    @staticmethod
    def normalize_phone(phone):
        """نرمالایز کردن شماره تلفن"""
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        if not cleaned.startswith('98') and len(cleaned) == 10:
            cleaned = '98' + cleaned
        return cleaned


class User(AbstractBaseUser, PermissionsMixin):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user' 
    
    def __str__(self):
        return f"{self.phone} - {self.username}"
    
    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = UserManager.normalize_phone(self.phone)
        super().save(*args, **kwargs)


class OTP(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='otps')
    phone = models.CharField(max_length=20, db_index=True)  
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_otp'
        indexes = [
            models.Index(fields=['phone', 'code', 'is_used']),  
            models.Index(fields=['expires_at']), 
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = UserManager.normalize_phone(self.phone)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=2)
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_code(cls):
        """تولید کد 6 رقمی"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """بررسی اعتبار کد"""
        return not self.is_used and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"{self.phone} - {self.code} - {self.expires_at}"


# apps/accounts/models.py

# from django.db import models
# import uuid


# class OTP(models.Model):
#     """کدهای OTP"""
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     phone = models.CharField(max_length=20)
#     code = models.CharField(max_length=6)
#     expires_at = models.DateTimeField()
#     is_used = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.phone} - {self.code}"