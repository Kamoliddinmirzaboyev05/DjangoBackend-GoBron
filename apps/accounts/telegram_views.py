import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .models import CustomUser

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """Telegram webhook uchun view"""
    
    def post(self, request):
        try:
            # JSON ma'lumotlarni olish
            data = json.loads(request.body.decode('utf-8'))
            
            # Update ni qayta ishlash
            self.process_update(data)
            
            return JsonResponse({'ok': True})
            
        except Exception as e:
            logger.error(f"Webhook xatolik: {e}")
            return JsonResponse({'ok': False, 'error': str(e)})
    
    def process_update(self, update):
        """Telegram update ni qayta ishlash"""
        if 'message' not in update:
            return
            
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # Foydalanuvchi ma'lumotlari
        user_info = message['from']
        
        if text == '/start':
            self.handle_start_command(chat_id, user_info)
        elif text == '/help':
            self.send_help_message(chat_id)
        elif 'contact' in message:
            self.handle_contact_shared(chat_id, message['contact'])
    
    def handle_start_command(self, chat_id, user_info):
        """Start komandasi"""
        welcome_text = """🏟️ <b>Football Booking botiga xush kelibsiz!</b>

Bu bot orqali siz telefon raqamingizni tasdiqlashingiz mumkin.

<b>Ro'yxatdan o'tish uchun:</b>
1. Mobil ilovada telefon raqamingizni kiriting
2. Bot sizga 4 xonali kod yuboradi
3. Kodni ilovaga kiriting

<b>Telefon raqamingizni ulash uchun:</b>
Quyidagi tugmani bosing va telefon raqamingizni yuboring 👇"""

        # Telefon raqamini so'rash uchun keyboard
        keyboard = {
            'keyboard': [
                [{'text': '📱 Telefon raqamini yuborish', 'request_contact': True}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        self.send_message(chat_id, welcome_text, keyboard)
    
    def handle_contact_shared(self, chat_id, contact):
        """Telefon raqami yuborilganda"""
        phone = contact.get('phone_number', '')
        
        if phone:
            # Telefon raqamini formatlash
            from .utils import format_phone_number
            formatted_phone = format_phone_number(phone)
            
            # Foydalanuvchini topish yoki yaratish
            try:
                user = CustomUser.objects.get(phone=formatted_phone)
                user.telegram_chat_id = str(chat_id)
                user.save()
                
                success_text = f"""✅ <b>Muvaffaqiyat!</b>

Sizning hisobingiz Telegram bilan bog'landi.
📱 Telefon: <code>{formatted_phone}</code>

Endi siz OTP kodlarini shu bot orqali olishingiz mumkin."""
                
                self.send_message(chat_id, success_text)
                
            except CustomUser.DoesNotExist:
                info_text = f"""📱 <b>Telefon raqami saqlandi</b>

Telefon: <code>{formatted_phone}</code>

Endi siz mobil ilovada ro'yxatdan o'tishingiz mumkin. OTP kodlar shu bot orqali yuboriladi."""
                
                self.send_message(chat_id, info_text)
        else:
            error_text = "❌ Telefon raqami topilmadi. Iltimos, qaytadan urinib ko'ring."
            self.send_message(chat_id, error_text)
    
    def send_help_message(self, chat_id):
        """Yordam xabari"""
        help_text = """🤖 <b>Bot buyruqlari:</b>

/start - Botni ishga tushirish
/help - Yordam

<b>📱 Qanday ishlaydi:</b>
1. Telefon raqamingizni bot bilan ulang
2. Mobil ilovada ro'yxatdan o'ting
3. OTP kodlarni bot orqali oling

<b>📞 Qo'llab-quvvatlash:</b>
Agar muammo bo'lsa, administrator bilan bog'laning."""

        self.send_message(chat_id, help_text)
    
    def send_message(self, chat_id, text, keyboard=None):
        """Xabar yuborish"""
        import requests
        
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return False
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if keyboard:
            data['reply_markup'] = keyboard
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
            return False


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    view = TelegramWebhookView()
    return view.post(request)