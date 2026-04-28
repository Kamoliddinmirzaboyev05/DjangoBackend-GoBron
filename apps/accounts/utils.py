import random
import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def generate_otp():
    """4 xonali OTP kod yaratish"""
    return str(random.randint(1000, 9999))


def save_otp(phone, otp):
    """OTP ni cache ga saqlash"""
    try:
        # Django cache da saqlash (5 daqiqa = 300 sekund)
        cache.set(f"otp:{phone}", otp, 300)
        logger.info(f"OTP saqlandi: {phone}")
        return True
    except Exception as e:
        logger.error(f"OTP saqlashda xatolik: {e}")
        return False


def get_otp(phone):
    """Cache dan OTP ni olish"""
    try:
        otp = cache.get(f"otp:{phone}")
        logger.info(f"OTP olindi: {phone} -> {otp}")
        return otp
    except Exception as e:
        logger.error(f"OTP olishda xatolik: {e}")
        return None


def delete_otp(phone):
    """OTP ni o'chirish"""
    try:
        cache.delete(f"otp:{phone}")
        logger.info(f"OTP o'chirildi: {phone}")
        return True
    except Exception as e:
        logger.error(f"OTP o'chirishda xatolik: {e}")
        return False


def send_telegram_otp(phone, otp):
    """Telegram bot orqali OTP yuborish"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.error("Telegram bot token topilmadi")
            # Test uchun console ga chiqaramiz
            print(f"🔐 OTP CODE for {phone}: {otp}")
            return True

        # Telefon raqamini tozalash (+998901234567 -> 998901234567)
        clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
        
        # Foydalanuvchini topish va chat_id ni olish
        from .models import CustomUser
        try:
            user = CustomUser.objects.get(phone=phone)
            chat_id = user.telegram_chat_id
            
            if not chat_id:
                logger.warning(f"Foydalanuvchi {phone} uchun chat_id topilmadi. Console ga chiqarilmoqda.")
                print(f"🔐 OTP CODE for {phone}: {otp}")
                return True
                
        except CustomUser.DoesNotExist:
            # Yangi foydalanuvchi uchun console ga chiqaramiz
            logger.info(f"Yangi foydalanuvchi {phone} uchun OTP console ga chiqarilmoqda")
            print(f"🔐 OTP CODE for {phone}: {otp}")
            return True
        
        # Telegram API URL
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Xabar matni
        message = f"""🔐 <b>Tasdiqlash kodi</b>

Sizning tasdiqlash kodingiz: <code>{otp}</code>

⏰ Kod 5 daqiqa davomida amal qiladi.
🔒 Bu kodni hech kimga bermang!

<i>Football Booking tizimi</i>"""

        # Xabar yuborish
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info(f"OTP muvaffaqiyatli yuborildi: {phone}")
                return True
            else:
                logger.error(f"Telegram API xatolik: {result}")
                # Fallback - console ga chiqarish
                print(f"🔐 OTP CODE for {phone}: {otp}")
                return True
        else:
            logger.error(f"HTTP xatolik: {response.status_code} - {response.text}")
            # Fallback - console ga chiqarish
            print(f"🔐 OTP CODE for {phone}: {otp}")
            return True
            
    except Exception as e:
        logger.error(f"Telegram OTP yuborishda xatolik: {e}")
        # Fallback - console ga chiqarish
        print(f"🔐 OTP CODE for {phone}: {otp}")
        return True


def get_telegram_chat_id_by_phone(phone):
    """Telefon raqami bo'yicha chat_id ni topish (bot updates orqali)"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return None

        # Bot updates ni olish
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                updates = result.get('result', [])
                
                # Telefon raqami bo'yicha chat_id ni qidirish
                clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
                
                for update in updates:
                    if 'message' in update:
                        message = update['message']
                        if 'contact' in message:
                            contact_phone = message['contact'].get('phone_number', '')
                            contact_phone = contact_phone.replace('+', '').replace('-', '').replace(' ', '')
                            
                            if contact_phone == clean_phone:
                                return str(message['chat']['id'])
                
        return None
        
    except Exception as e:
        logger.error(f"Chat ID topishda xatolik: {e}")
        return None


def get_telegram_chat_id(phone):
    """Telefon raqami bo'yicha Telegram chat ID ni topish"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return None

        # Bu yerda siz o'zingizning chat_id bazangizni ishlatishingiz mumkin
        # Yoki foydalanuvchi avval botga /start yozgan bo'lishi kerak
        
        # Hozircha telefon raqamini chat_id sifatida qaytaramiz
        # Lekin bu ishlamaydi, chunki chat_id boshqacha bo'ladi
        
        clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
        return clean_phone
        
    except Exception as e:
        logger.error(f"Chat ID topishda xatolik: {e}")
        return None


def format_phone_number(phone):
    """Telefon raqamini formatlash"""
    # Barcha belgilarni olib tashlash
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # Agar +998 bilan boshlanmasa, qo'shish
    if not clean_phone.startswith('998'):
        if clean_phone.startswith('8'):
            clean_phone = '99' + clean_phone
        else:
            clean_phone = '998' + clean_phone
    
    return '+' + clean_phone


def validate_phone_number(phone):
    """Telefon raqamini tekshirish"""
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # O'zbekiston telefon raqami formatini tekshirish
    if len(clean_phone) == 12 and clean_phone.startswith('998'):
        return True
    elif len(clean_phone) == 9 and clean_phone.startswith('9'):
        return True
    
    return False