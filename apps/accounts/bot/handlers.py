"""Telegram bot handlerlari"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.db import sync_to_async

from ..models import CustomUser, MagicToken, UserSession
from .keyboards import (
    get_role_selection_keyboard,
    get_contact_keyboard,
    get_magic_link_keyboard,
    get_main_menu_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


class RegistrationStates(StatesGroup):
    """Ro'yxatdan o'tish holatlari"""
    waiting_for_role = State()
    waiting_for_contact = State()
    waiting_for_name = State()


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
    """Start buyrug'i handler"""
    try:
        telegram_id = message.from_user.id
        telegram_username = message.from_user.username
        
        # Foydalanuvchini topish
        user = await get_user_by_telegram_id(telegram_id)
        
        if user:
            # Mavjud foydalanuvchi
            await existing_user_flow(message, user, state)
        else:
            # Yangi foydalanuvchi
            await new_user_flow(message, state, telegram_username)
            
    except Exception as e:
        logger.error(f"Start handler error: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n"
            "Agar muammo davom etsa, qo'llab-quvvatlash bilan bog'laning."
        )


async def new_user_flow(message: Message, state: FSMContext, telegram_username=None):
    """Yangi foydalanuvchi uchun oqim"""
    await state.update_data(telegram_username=telegram_username)
    
    welcome_text = """🎉 <b>GoBron platformasiga xush kelibsiz!</b>

Bu yerda siz:
⚽ Futbol maydonlarini topishingiz
📅 Maydonlarni bron qilishingiz
🏟️ O'z maydonlaringizni boshqarishingiz mumkin

Davom etish uchun rolni tanlang:"""

    await message.answer(
        welcome_text,
        reply_markup=get_role_selection_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_role)


async def existing_user_flow(message: Message, user, state: FSMContext):
    """Mavjud foydalanuvchi uchun oqim"""
    await state.clear()
    
    # Magic Token yaratish
    magic_token = await create_magic_token(user)
    
    # Sessiya ma'lumotlarini saqlash
    await save_user_session(user, message.from_user.id, {
        'last_login': message.date.isoformat(),
        'username': message.from_user.username
    })
    
    welcome_text = f"""👋 <b>Salom, {user.full_name or user.phone_number}!</b>

Sizning rolingiz: <b>{user.get_user_role_display()}</b>

Ilovaga kirish uchun quyidagi tugmani bosing:"""

    await message.answer(
        welcome_text,
        reply_markup=get_magic_link_keyboard(magic_token.token, user.user_role),
        parse_mode="HTML"
    )


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
    """Kontakt handler"""
    try:
        contact: Contact = message.contact
        phone_number = format_phone_number(contact.phone_number)
        
        # Telefon raqami mavjudligini tekshirish
        existing_user = await get_user_by_phone(phone_number)
        if existing_user:
            # Telegram ID ni yangilash
            await update_user(existing_user, telegram_id=message.from_user.id)
            await existing_user_flow(message, existing_user, state)
            return
        
        # Yangi foydalanuvchi uchun ism so'rash
        await state.update_data(phone_number=phone_number)
        
        text = """📝 <b>Ism-familiyangizni kiriting:</b>

Masalan: Akmal Karimov"""

        await message.answer(text, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Contact handler error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message(RegistrationStates.waiting_for_name, F.text)
async def name_handler(message: Message, state: FSMContext):
    """Ism handler"""
    try:
        full_name = message.text.strip()
        
        if len(full_name) < 2:
            await message.answer("❌ Ism juda qisqa. Iltimos, to'liq ism-familiyangizni kiriting.")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        data = await state.get_data()
        
        # Foydalanuvchi yaratish
        user = await create_user(
            telegram_id=message.from_user.id,
            phone_number=data['phone_number'],
            user_role=data['user_role'],
            full_name=full_name,
            telegram_username=data.get('telegram_username')
        )
        
        # Magic Token yaratish
        magic_token = await create_magic_token(user)
        
        # Sessiya saqlash
        await save_user_session(user, message.from_user.id, {
            'registration_date': message.date.isoformat(),
            'username': message.from_user.username
        })
        
        success_text = f"""🎉 <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>

👤 <b>Ism:</b> {full_name}
📱 <b>Telefon:</b> {data['phone_number']}
⚽ <b>Rol:</b> {user.get_user_role_display()}

Ilovaga kirish uchun quyidagi tugmani bosing:"""

        await message.answer(
            success_text,
            reply_markup=get_magic_link_keyboard(magic_token.token, user.user_role),
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Name handler error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.message(Command("help"))
async def help_handler(message: Message):
    """Yordam buyrug'i"""
    help_text = """🤖 <b>GoBron Bot Yordam</b>

<b>Buyruqlar:</b>
/start - Botni ishga tushirish
/help - Bu yordam xabari
/profile - Profil ma'lumotlari

<b>Bot haqida:</b>
Bu bot GoBron platformasi uchun mo'ljallangan. Bu yerda siz futbol maydonlarini topishingiz va bron qilishingiz mumkin.

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


@router.message()
async def unknown_message_handler(message: Message):
    """Noma'lum xabar handler"""
    await message.answer(
        "🤔 Kechirasiz, bu buyruqni tushunmadim.\n"
        "Yordam uchun /help buyrug'ini ishlatib ko'ring."
    )