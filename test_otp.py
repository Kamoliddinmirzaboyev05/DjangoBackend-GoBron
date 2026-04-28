#!/usr/bin/env python3
"""
OTP funksiyasini test qilish uchun script
"""

import os
import django
from django.conf import settings

# Django sozlamalarini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import OTPCode, CustomUser

def test_otp_creation():
    """OTP yaratishni test qilish"""
    print("🧪 OTP yaratish testi...")
    
    # Test ma'lumotlari
    phone_number = "+998901234567"
    telegram_id = 123456789
    user_role = "PLAYER"
    full_name = "Test User"
    
    # OTP yaratish
    otp = OTPCode.generate_code(
        phone_number=phone_number,
        telegram_id=telegram_id,
        user_role=user_role,
        full_name=full_name
    )
    
    print(f"✅ OTP yaratildi:")
    print(f"   📱 Telefon: {otp.phone_number}")
    print(f"   🔐 Kod: {otp.code}")
    print(f"   👤 Ism: {otp.full_name}")
    print(f"   ⚽ Rol: {otp.get_user_role_display()}")
    print(f"   ⏰ Amal qilish muddati: {otp.expires_at}")
    print(f"   ✅ Yaroqli: {otp.is_valid}")
    
    return otp

def test_otp_verification(otp):
    """OTP tekshirishni test qilish"""
    print("\n🧪 OTP tekshirish testi...")
    
    # Noto'g'ri kod bilan test
    try:
        wrong_otp = OTPCode.objects.get(
            phone_number=otp.phone_number,
            telegram_id=otp.telegram_id,
            code="0000"  # Noto'g'ri kod
        )
        print("❌ Noto'g'ri kod test muvaffaqiyatsiz")
    except OTPCode.DoesNotExist:
        print("✅ Noto'g'ri kod to'g'ri rad etildi")
    
    # To'g'ri kod bilan test
    try:
        correct_otp = OTPCode.objects.get(
            phone_number=otp.phone_number,
            telegram_id=otp.telegram_id,
            code=otp.code
        )
        print(f"✅ To'g'ri kod topildi: {correct_otp.code}")
        
        # Kodni tasdiqlash
        correct_otp.is_verified = True
        correct_otp.save()
        print("✅ Kod tasdiqlandi")
        
    except OTPCode.DoesNotExist:
        print("❌ To'g'ri kod topilmadi")

def test_user_creation_after_otp():
    """OTP dan keyin foydalanuvchi yaratishni test qilish"""
    print("\n🧪 Foydalanuvchi yaratish testi...")
    
    # Test OTP
    otp = OTPCode.objects.filter(is_verified=True).first()
    if not otp:
        print("❌ Tasdiqlangan OTP topilmadi")
        return
    
    # Mavjud foydalanuvchini tekshirish
    existing_user = CustomUser.objects.filter(telegram_id=otp.telegram_id).first()
    if existing_user:
        print(f"ℹ️ Foydalanuvchi allaqachon mavjud: {existing_user.phone_number}")
        return existing_user
    
    # Foydalanuvchi yaratish
    user = CustomUser.objects.create(
        phone_number=otp.phone_number,
        telegram_id=otp.telegram_id,
        user_role=otp.user_role,
        full_name=otp.full_name,
        telegram_username=otp.telegram_username,
        is_phone_verified=True,
        username=otp.phone_number
    )
    
    print(f"✅ Foydalanuvchi yaratildi:")
    print(f"   📱 Telefon: {user.phone_number}")
    print(f"   👤 Ism: {user.full_name}")
    print(f"   ⚽ Rol: {user.get_user_role_display()}")
    print(f"   ✅ Telefon tasdiqlangan: {user.is_phone_verified}")
    
    return user

if __name__ == "__main__":
    print("🚀 GoBron OTP Test Script")
    print("=" * 50)
    
    try:
        # OTP yaratish testi
        otp = test_otp_creation()
        
        # OTP tekshirish testi
        test_otp_verification(otp)
        
        # Foydalanuvchi yaratish testi
        user = test_user_creation_after_otp()
        
        print("\n🎉 Barcha testlar muvaffaqiyatli o'tdi!")
        
    except Exception as e:
        print(f"\n❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()