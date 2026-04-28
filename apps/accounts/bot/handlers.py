"""Telegram bot handlerlari"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.db import sync_to_async

from ..models import CustomUser, MagicToken, UserSession, OTPCode
from .keyboards import (
    get_role_selection_keyboard,
    get_contact_keyboard,
    get_magic_link_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


class RegistrationStates(StatesGroup):
    """Ro'yxatdan o'tish holatlari"""
    waiting_for_role = State()
    waiting_for_contact = State()
    waiting_for_name = State()
    waiting_for_otp = State()


# Database operatsiyalari
@sync_to_async
def get_user_by_telegram_id(telegram_id):
    """Telegram ID bo'yicha foydalanuvchini topish"""
    try:
        return CustomUser.objects.get(telegram_id=telegram_id)
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def get_user_by_phone(phone_number):
    """Telefon raqami bo'yicha foydalanuvchini topish"""
    try:
        return CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def create_user(telegram_id, phone_number, user_role, full_name=None, telegram_username=None):
    """Yangi foydalanuvchi yaratish"""
    user = CustomUser.objects.create(
        telegram_id=telegram_id,
        phone_number=phone_number,
        user_role=user_role,
        full_name=full_name,
        telegram_username=telegram_username,
        is_phone_verified=True,
        username=phone_number  # Username sifatida telefon raqamini ishlatamiz
    )
    return user


@sync_to_async
def update_user(user, **kwargs):
    """Foydalanuvchini yangilash"""
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user


@sync_to_async
def create_magic_token(user):
    """Magic Token yaratish"""
    # Eski tokenlarni o'chirish
    MagicToken.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Yangi token yaratish
    token = MagicToken.objects.create(user=user)
    return token


@sync_to_async
def save_user_session(user, telegram_id, session_data):
    """Foydalanuvchi sessiyasini saqlash"""
    session, created = UserSession.objects.get_or_create(
        user=user,
        telegram_id=telegram_id,
        defaults={'session_data': session_data}
    )
    if not created:
        session.session_data.update(session_data)
        session.save()
    return session


@sync_to_async
def send_otp_to_telegram(bot, telegram_id, otp_code):
    """OTP kodni Telegram orqali yuborish"""
    try:
        # Bu yerda haqiqiy OTP yuborish logikasi bo'lishi kerak
        # Hozircha faqat log qilamiz
        logger.info(f"OTP kod yuborildi: {telegram_id} -> {otp_code}")
        return True
    except Exception as e:
        logger.error(f"OTP yuborishda xatolik: {e}")
        return False


def format_phone_number(phone):
    """Telefon raqamini formatlash"""
    # Barcha belgilarni olib tashlash
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # O'zbekiston formatiga keltirish
    if clean_phone.startswith('998'):
        return f"+{clean_phone}"
    elif clean_phone.startswith('8') and len(clean_phone) == 9:
        return f"+99{clean_phone}"
    elif len(clean_phone) == 9:
        return f"+998{clean_phone}"
    else:
        return f"+{clean_phone}"


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Start buyrug'i handler - Silent Auth"""
    try:
        telegram_id = message.from_user.id
        telegram_username = message.from_user.username
        
        # Foydalanuvchini topish
        user = await get_user_by_telegram_id(telegram_id)
        
        if user:
            # Mavjud foydalanuvchi - Silent Auth
            await silent_auth_flow(message, user, state)
        else:
            # Yangi foydalanuvchi - Registration flow
            await new_user_flow(message, state, telegram_username)
            
    except Exception as e:
        logger.error(f"Start handler error: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n"
            "Agar muammo davom etsa, qo'llab-quvvatlash bilan bog'laning."
        )


async def silent_auth_flow(message: Message, user, state: FSMContext):
    """Mavjud foydalanuvchi uchun Silent Auth"""
    await state.clear()
    
    # Magic Token yaratish
    magic_token = await create_magic_token(user)
    
    # Sessiya ma'lumotlarini saqlash
    await save_user_session(user, message.from_user.id, {
        'last_login': message.date.isoformat(),
        'username': message.from_user.username
    })
    
    # Foydalanuvchi roliga qarab yo'naltirish
    if user.user_role == 'PLAYER':
        app_type = "🎮 Telegram Mini App"
        description = "Maydonlarni ko'rish va bron qilish uchun"
    else:  # OWNER
        app_type = "🏢 PWA Boshqaruv Paneli"
        description = "Maydonlaringizni boshqarish uchun"
    
    welcome_text = f"""👋 <b>Salom, {user.full_name or user.phone_number}!</b>

🎯 <b>Sizning rolingiz:</b> {user.get_user_role_display()}
📱 <b>Ilovangiz:</b> {app_type}

{description}

<i>Quyidagi tugmani bosib ilovaga kiring:</i>"""

    await message.answer(
        welcome_text,
        reply_markup=get_magic_link_keyboard(magic_token.token, user.user_role),
        parse_mode="HTML"
    )


async def new_user_flow(message: Message, state: FSMContext, telegram_username=None):
    """Yangi foydalanuvchi uchun ro'yxatdan o'tish"""
    await state.update_data(telegram_username=telegram_username)
    
    welcome_text = """🎉 <b>GoBron platformasiga xush kelibsiz!</b>

Bu yerda siz:
⚽ Futbol maydonlarini topishingiz
📅 Maydonlarni bron qilishingiz
🏟️ O'z maydonlaringizni boshqarishingiz mumkin

<b>Davom etish uchun rolni tanlang:</b>"""

    await message.answer(
        welcome_text,
        reply_markup=get_role_selection_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_role)


@router.callback_query(F.data.startswith("role:"))
async def role_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Rol tanlash handler"""
    try:
        role = callback.data.split(":")[1]
        await state.update_data(user_role=role)
        
        role_name = "Futbolchi" if role == "PLAYER" else "Maydon egasi"
        
        text = f"""✅ <b>Rol tanlandi: {role_name}</b>

Endi telefon raqamingizni yuboring:"""

        await callback.message.edit_text(
            text,
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_contact)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Role selection error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)


@router.message(RegistrationStates.waiting_for_contact, F.contact)
async def contact_handler(message: Message, state: FSMContext):
    """Kontakt handler - OTP yuborish"""
    try:
        contact: Contact = message.contact
        phone_number = format_phone_number(contact.phone_number)
        
        # Telefon raqami mavjudligini tekshirish
        existing_user = await get_user_by_phone(phone_number)
        if existing_user:
            # Telegram ID ni yangilash va Silent Auth
            await update_user(existing_user, telegram_id=message.from_user.id)
            await silent_auth_flow(message, existing_user, state)
            return
        
        # Yangi foydalanuvchi uchun ism so'rash
        await state.update_data(phone_number=phone_number)
        
        text = """📝 <b>Ism-familiyangizni kiriting:</b>

<i>Masalan: Akmal Karimov</i>"""

        await message.answer(text, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Contact handler error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message(RegistrationStates.waiting_for_name, F.text)
async def name_handler(message: Message, state: FSMContext):
    """Ism handler - OTP yuborish"""
    try:
        full_name = message.text.strip()
        
        if len(full_name) < 2:
            await message.answer("❌ Ism juda qisqa. Iltimos, to'liq ism-familiyangizni kiriting.")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        data = await state.get_data()
        
        # OTP kod yaratish va yuborish
        otp = await create_otp_code(
            phone_number=data['phone_number'],
            telegram_id=message.from_user.id,
            user_role=data['user_role'],
            full_name=full_name,
            telegram_username=data.get('telegram_username')
        )
        
        # OTP kodni Telegram orqali yuborish
        otp_text = f"""🔐 <b>Tasdiqlash kodi:</b>

<code>{otp.code}</code>

📱 <b>Telefon raqamingiz:</b> {data['phone_number']}
⏰ <b>Kod 5 daqiqa amal qiladi</b>

Kodni quyidagi xabarga yozing:"""

        await message.answer(otp_text, parse_mode="HTML")
        
        # State ni OTP kutish holatiga o'tkazish
        await state.set_state(RegistrationStates.waiting_for_otp)
        
    except Exception as e:
        logger.error(f"Name handler error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message(RegistrationStates.waiting_for_otp, F.text)
async def otp_handler(message: Message, state: FSMContext):
    """OTP kod tekshirish handler"""
    try:
        otp_code = message.text.strip()
        
        # Kod formatini tekshirish
        if not otp_code.isdigit() or len(otp_code) != 4:
            await message.answer("❌ Kod 4 ta raqamdan iborat bo'lishi kerak. Qaytadan kiriting:")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        data = await state.get_data()
        
        # OTP kodni tekshirish
        otp, error = await verify_otp_code(
            phone_number=data['phone_number'],
            telegram_id=message.from_user.id,
            code=otp_code
        )
        
        if error:
            await message.answer(f"❌ {error}")
            
            # Agar juda ko'p urinish bo'lsa, qaytadan boshlash
            if "Juda ko'p" in error:
                await message.answer("🔄 Qaytadan boshlash uchun /start buyrug'ini yuboring.")
                await state.clear()
            return
        
        if not otp:
            await message.answer("❌ Noto'g'ri kod. Qaytadan kiriting:")
            return
        
        # Foydalanuvchi yaratish
        user = await create_user(
            telegram_id=message.from_user.id,
            phone_number=otp.phone_number,
            user_role=otp.user_role,
            full_name=otp.full_name,
            telegram_username=otp.telegram_username
        )
        
        # Magic Token yaratish
        magic_token = await create_magic_token(user)
        
        # Sessiya saqlash
        await save_user_session(user, message.from_user.id, {
            'registration_date': message.date.isoformat(),
            'username': message.from_user.username,
            'otp_verified': True
        })
        
        # Foydalanuvchi roliga qarab yo'naltirish
        if user.user_role == 'PLAYER':
            app_type = "🎮 Telegram Mini App"
            description = "Maydonlarni ko'rish va bron qilish uchun"
        else:  # OWNER
            app_type = "🏢 PWA Boshqaruv Paneli"
            description = "Maydonlaringizni boshqarish uchun"
        
        success_text = f"""🎉 <b>Telefon raqami tasdiqlandi!</b>

✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>

👤 <b>Ism:</b> {otp.full_name}
📱 <b>Telefon:</b> {otp.phone_number}
⚽ <b>Rol:</b> {user.get_user_role_display()}
🎯 <b>Ilovangiz:</b> {app_type}

{description}

<i>Quyidagi tugmani bosib ilovaga kiring:</i>"""

        await message.answer(
            success_text,
            reply_markup=get_magic_link_keyboard(magic_token.token, user.user_role),
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"OTP handler error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message(Command("help"))
async def help_handler(message: Message):
    """Yordam buyrug'i"""
    help_text = """🤖 <b>GoBron Bot Yordam</b>

<b>Buyruqlar:</b>
/start - Botni ishga tushirish
/help - Bu yordam xabari
/profile - Profil ma'lumotlari
/resend_otp - OTP kodni qayta yuborish

<b>Bot haqida:</b>
Bu bot GoBron platformasi uchun mo'ljallangan. Bu yerda siz futbol maydonlarini topishingiz va bron qilishingiz mumkin.

<b>Ro'yxatdan o'tish:</b>
1. Rolni tanlang (Futbolchi yoki Maydon egasi)
2. Telefon raqamingizni yuboring
3. Ism-familiyangizni kiriting
4. SMS orqali kelgan 4 xonali kodni kiriting
5. Ilovaga kiring

<b>Qo'llab-quvvatlash:</b>
Agar savollaringiz bo'lsa, @support ga murojaat qiling."""

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("profile"))
async def profile_handler(message: Message):
    """Profil buyrug'i"""
    try:
        user = await get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.answer(
                "❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'ini ishlatib ro'yxatdan o'ting."
            )
            return
        
        profile_text = f"""👤 <b>Profil ma'lumotlari</b>

📱 <b>Telefon:</b> {user.phone_number}
👤 <b>Ism:</b> {user.full_name or 'Kiritilmagan'}
⚽ <b>Rol:</b> {user.get_user_role_display()}
📅 <b>Ro'yxatdan o'tgan:</b> {user.date_joined.strftime('%d.%m.%Y')}
✅ <b>Telefon tasdiqlangan:</b> {'Ha' if user.is_phone_verified else 'Yo\'q'}"""

        await message.answer(profile_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Profile handler error: {e}")
        await message.answer("❌ Profil ma'lumotlarini olishda xatolik yuz berdi.")


@router.message(Command("resend_otp"))
async def resend_otp_handler(message: Message, state: FSMContext):
    """OTP kodni qayta yuborish"""
    try:
        # Foydalanuvchi state ni tekshirish
        current_state = await state.get_state()
        if current_state != RegistrationStates.waiting_for_otp:
            await message.answer(
                "❌ Hozir OTP kutilmayapti. Ro'yxatdan o'tish uchun /start buyrug'ini ishlatib ko'ring."
            )
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        data = await state.get_data()
        if not data.get('phone_number'):
            await message.answer("❌ Ma'lumotlar topilmadi. Qaytadan /start buyrug'ini ishlatib ko'ring.")
            await state.clear()
            return
        
        # Yangi OTP kod yaratish
        otp = await create_otp_code(
            phone_number=data['phone_number'],
            telegram_id=message.from_user.id,
            user_role=data['user_role'],
            full_name=data.get('full_name'),
            telegram_username=data.get('telegram_username')
        )
        
        # Yangi kodni yuborish
        otp_text = f"""🔐 <b>Yangi tasdiqlash kodi:</b>

<code>{otp.code}</code>

📱 <b>Telefon raqamingiz:</b> {data['phone_number']}
⏰ <b>Kod 5 daqiqa amal qiladi</b>

Kodni quyidagi xabarga yozing:"""

        await message.answer(otp_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message()
async def unknown_message_handler(message: Message):
    """Noma'lum xabar handler"""
    await message.answer(
        "🤔 Kechirasiz, bu buyruqni tushunmadim.\n"
        "Yordam uchun /help buyrug'ini ishlatib ko'ring."
    )