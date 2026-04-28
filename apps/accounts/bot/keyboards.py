"""Telegram bot klaviaturalari"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_role_selection_keyboard():
    """Rol tanlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚽ Futbolchiman", 
                callback_data="role:PLAYER"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏟️ Maydon egasiman", 
                callback_data="role:OWNER"
            )
        ]
    ])
    return keyboard


def get_contact_keyboard():
    """Telefon raqamini yuborish klaviaturasi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Telefon raqamini yuborish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_magic_link_keyboard(token, user_role):
    """Magic Link klaviaturasi"""
    if user_role == 'PLAYER':
        # Telegram Mini App
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Ilovani ochish",
                    web_app={
                        "url": f"https://t.me/GoBronBot/app?startapp={token}"
                    }
                )
            ]
        ])
    else:  # OWNER
        # PWA ilovasi
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏢 Boshqaruv paneli",
                    url=f"https://gobron.uz/verify-auth?token={token}"
                )
            ]
        ])
    
    return keyboard


def get_main_menu_keyboard(user_role):
    """Asosiy menyu klaviaturasi"""
    if user_role == 'PLAYER':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚽ Maydon topish",
                    callback_data="action:find_stadium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Mening bronlarim",
                    callback_data="action:my_bookings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Profil",
                    callback_data="action:profile"
                )
            ]
        ])
    else:  # OWNER
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏟️ Mening maydonlarim",
                    callback_data="action:my_stadiums"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="action:statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Profil",
                    callback_data="action:profile"
                )
            ]
        ])
    
    return keyboard