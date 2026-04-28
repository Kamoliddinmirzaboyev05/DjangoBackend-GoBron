import uuid
import random
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(UserManager):
    """Custom User Manager"""
    
    def create_user(self, phone_number, telegram_id=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Telefon raqami kiritilishi shart')
        
        extra_fields.setdefault('username', phone_number)
        user = self.model(phone_number=phone_number, telegram_id=telegram_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, telegram_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_role', 'OWNER')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak.')
        
        return self.create_user(phone_number, telegram_id, password, **extra_fields)


class CustomUser(AbstractUser):
    """GoBron foydalanuvchi modeli"""
    
    USER_ROLE_CHOICES = [
        ('PLAYER', 'Futbolchi'),
        ('OWNER', 'Maydon egasi'),
    ]

    # Asosiy maydonlar
    phone_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='Telefon raqami'
    )
    telegram_id = models.BigIntegerField(
        unique=True, 
        null=True, 
        blank=True,
        verbose_name='Telegram ID'
    )
    user_role = models.CharField(
        max_length=10, 
        choices=USER_ROLE_CHOICES, 
        default='PLAYER',
        verbose_name='Foydalanuvchi roli'
    )
    
    # Qo'shimcha maydonlar
    full_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='To\'liq ism'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='Avatar'
    )
    is_phone_verified = models.BooleanField(
        default=False, 
        verbose_name='Telefon tasdiqlangan'
    )
    telegram_username = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Telegram username'
    )
    
    # Login uchun telefon raqamini ishlatamiz
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.full_name or self.phone_number} ({self.get_user_role_display()})'

    @property
    def is_player(self):
        return self.user_role == 'PLAYER'

    @property
    def is_owner(self):
        return self.user_role == 'OWNER'

    def save(self, *args, **kwargs):
        # Username ni telefon raqamiga o'rnatish
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)


class MagicToken(models.Model):
    """Magic Link autentifikatsiya uchun token"""
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        verbose_name='Foydalanuvchi'
    )
    token = models.UUIDField(
        default=uuid.uuid4, 
        unique=True,
        verbose_name='Token'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='Ishlatilgan'
    )
    expires_at = models.DateTimeField(
        verbose_name='Amal qilish muddati'
    )

    class Meta:
        verbose_name = 'Magic Token'
        verbose_name_plural = 'Magic Tokenlar'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - {self.token}'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 10 daqiqa amal qiladi
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class Stadium(models.Model):
    """Futbol maydonlari"""
    
    owner = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_role': 'OWNER'},
        verbose_name='Egasi'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Maydon nomi'
    )
    address = models.TextField(
        verbose_name='Manzil'
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Soatlik narx (so\'m)'
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Tavsif'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Faol'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yangilangan vaqt'
    )

    class Meta:
        verbose_name = 'Stadion'
        verbose_name_plural = 'Stadionlar'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.owner.full_name}'


class UserSession(models.Model):
    """Foydalanuvchi sessiyalari (debugging uchun)"""
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        verbose_name='Foydalanuvchi'
    )
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID'
    )
    session_data = models.JSONField(
        default=dict,
        verbose_name='Sessiya ma\'lumotlari'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yangilangan vaqt'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi sessiyasi'
        verbose_name_plural = 'Foydalanuvchi sessiyalari'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.phone_number} - {self.telegram_id}'


class OTPCode(models.Model):
    """OTP kodlari telefon raqamini tasdiqlash uchun"""
    
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Telefon raqami'
    )
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID'
    )
    code = models.CharField(
        max_length=4,
        verbose_name='OTP kod'
    )
    user_role = models.CharField(
        max_length=10,
        choices=CustomUser.USER_ROLE_CHOICES,
        verbose_name='Foydalanuvchi roli'
    )
    full_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='To\'liq ism'
    )
    telegram_username = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram username'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Tasdiqlangan'
    )
    attempts = models.IntegerField(
        default=0,
        verbose_name='Urinishlar soni'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )
    expires_at = models.DateTimeField(
        verbose_name='Amal qilish muddati'
    )

    class Meta:
        verbose_name = 'OTP Kod'
        verbose_name_plural = 'OTP Kodlar'
        ordering = ['-created_at']
        unique_together = ['phone_number', 'telegram_id']

    def __str__(self):
        return f'{self.phone_number} - {self.code}'

    def save(self, *args, **kwargs):
        if not self.code:
            # 4 xonali tasodifiy kod yaratish
            self.code = str(random.randint(1000, 9999))
        
        if not self.expires_at:
            # 5 daqiqa amal qiladi
            self.expires_at = timezone.now() + timedelta(minutes=5)
        
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_verified and not self.is_expired and self.attempts < 3

    @classmethod
    def generate_code(cls, phone_number, telegram_id, user_role, full_name=None, telegram_username=None):
        """Yangi OTP kod yaratish"""
        # Eski kodlarni o'chirish
        cls.objects.filter(
            phone_number=phone_number,
            telegram_id=telegram_id
        ).delete()
        
        # Yangi kod yaratish
        otp = cls.objects.create(
            phone_number=phone_number,
            telegram_id=telegram_id,
            user_role=user_role,
            full_name=full_name,
            telegram_username=telegram_username
        )
        return otp
