# 🏟️ GoBron - Futbol Maydonlarini Bron Qilish Platformasi

## 📋 Loyiha Haqida

GoBron - Django (DRF) va aiogram 3.x kutubxonalari bilan qurilgan futbol maydonlarini bron qilish platformasi. Bu loyiha Telegram bot orqali autentifikatsiya va Magic Link tizimini qo'llab-quvvatlaydi.

## 🏗️ Arxitektura

### Ma'lumotlar Modeli

#### 1. CustomUser
```python
- phone_number (unique) - Telefon raqami
- telegram_id (unique) - Telegram ID
- user_role (PLAYER/OWNER) - Foydalanuvchi roli
- full_name - To'liq ism
- avatar - Avatar rasmi
- is_phone_verified - Telefon tasdiqlangan
- telegram_username - Telegram username
```

#### 2. MagicToken
```python
- user (FK) - Foydalanuvchi
- token (UUID) - Noyob token
- created_at - Yaratilgan vaqt
- expires_at - Amal qilish muddati (10 daqiqa)
- is_used - Ishlatilgan holat
```

#### 3. Stadium
```python
- owner (FK) - Maydon egasi
- name - Maydon nomi
- address - Manzil
- hourly_rate - Soatlik narx
- description - Tavsif
- is_active - Faol holat
```

## 🤖 Telegram Bot Logikasi

### Bot Oqimi

1. **Start buyrug'i** (`/start`)
   - Yangi foydalanuvchi: Rol tanlash (PLAYER/OWNER)
   - Mavjud foydalanuvchi: Magic Link yuborish

2. **Rol tanlash**
   - Inline tugmalar: "⚽ Futbolchiman" / "🏟️ Maydon egasiman"
   - Telefon raqamini so'rash

3. **Kontakt qabul qilish**
   - Telefon raqamini formatlash
   - Mavjud foydalanuvchini tekshirish
   - Yangi foydalanuvchi uchun ism so'rash

4. **Magic Link yaratish**
   - PLAYER: Telegram Mini App linki
   - OWNER: PWA ilovasi linki

### Bot Buyruqlari

- `/start` - Botni ishga tushirish
- `/help` - Yordam ma'lumotlari
- `/profile` - Profil ko'rish

## 🔐 Autentifikatsiya Tizimi

### Magic Token Flow

1. **Token yaratish**: Bot orqali foydalanuvchi uchun Magic Token yaratiladi
2. **Link yuborish**: 
   - PLAYER: `https://t.me/GoBronBot/app?startapp=TOKEN`
   - OWNER: `https://gobron.uz/verify-auth?token=TOKEN`
3. **Token tasdiqlash**: `/api/auth/verify-token/` endpoint orqali
4. **JWT olish**: Muvaffaqiyatli tasdiqdan keyin access va refresh tokenlar

### API Endpoints

#### Magic Token Autentifikatsiya
```http
POST /api/auth/verify-token/
Content-Type: application/json

{
  "token": "uuid-token"
}
```

**Response:**
```json
{
  "message": "Muvaffaqiyatli autentifikatsiya",
  "user": {
    "id": 1,
    "phone_number": "+998901234567",
    "user_role": "OWNER",
    "full_name": "Admin User"
  },
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token"
}
```

#### Profil
```http
GET /api/auth/profile/
Authorization: Bearer <access-token>
```

#### Stadionlar
```http
GET /api/auth/stadiums/
Authorization: Bearer <access-token>
```

## 🚀 O'rnatish va Ishga Tushirish

### 1. Kerakli paketlar
```bash
pip install -r requirements.txt
```

### 2. Ma'lumotlar bazasi
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Superuser yaratish
```bash
python manage.py shell -c "
from apps.accounts.models import CustomUser
user = CustomUser.objects.create_superuser(
    phone_number='+998901234567',
    telegram_id=123456789,
    password='strongpassword123',
    full_name='Admin User'
)
"
```

### 4. Django server
```bash
python manage.py runserver
```

### 5. Telegram bot
```bash
python manage.py run_bot
```

## ⚙️ Konfiguratsiya

### .env fayli
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Telegram Bot
TELEGRAM_BOT_TOKEN=8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo
TELEGRAM_BOT_USERNAME=GoBronBot

# URLs
TELEGRAM_MINI_APP_URL=https://t.me/GoBronBot/app
PWA_APP_URL=https://gobron.uz/verify-auth

# Redis
REDIS_URL=redis://localhost:6379/0
```

## 📱 Bot Klaviaturalari

### Rol tanlash
```python
def get_role_selection_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Futbolchiman", callback_data="role:PLAYER")],
        [InlineKeyboardButton(text="🏟️ Maydon egasiman", callback_data="role:OWNER")]
    ])
```

### Telefon raqami
```python
def get_contact_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📱 Telefon raqamini yuborish", request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
```

### Magic Link
```python
def get_magic_link_keyboard(token, user_role):
    if user_role == 'PLAYER':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎮 Ilovani ochish",
                web_app={"url": f"https://t.me/GoBronBot/app?startapp={token}"}
            )]
        ])
    else:  # OWNER
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🏢 Boshqaruv paneli",
                url=f"https://gobron.uz/verify-auth?token={token}"
            )]
        ])
```

## 🔧 Texnik Xususiyatlar

### Asinxron Database Operatsiyalari
```python
@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        return CustomUser.objects.get(telegram_id=telegram_id)
    except CustomUser.DoesNotExist:
        return None

@sync_to_async
def create_magic_token(user):
    MagicToken.objects.filter(user=user, is_used=False).update(is_used=True)
    token = MagicToken.objects.create(user=user)
    return token
```

### Xatoliklarni Qayta Ishlash
```python
async def start_handler(message: Message, state: FSMContext):
    try:
        # Bot logikasi
        pass
    except Exception as e:
        logger.error(f"Start handler error: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
        )
```

## 📊 Admin Panel

### Unfold Admin
- Zamonaviy UI/UX
- O'zbek tilida
- Foydalanuvchilar boshqaruvi
- Magic Token monitoring
- Stadion boshqaruvi

### Admin URL
```
http://localhost:8000/admin/
```

## 🧪 Test Qilish

### Magic Token Test
```bash
# Token yaratish
python manage.py shell -c "
from apps.accounts.models import CustomUser, MagicToken
user = CustomUser.objects.first()
token = MagicToken.objects.create(user=user)
print(f'Token: {token.token}')
"

# API test
curl -X POST http://localhost:8000/api/auth/verify-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "your-token-here"}'
```

### Bot Test
1. Telegram da @GoBronBot ga `/start` yuboring
2. Rolni tanlang
3. Telefon raqamini yuboring
4. Magic Link tugmasini bosing

## 📚 API Dokumentatsiyasi

### Swagger UI
```
http://localhost:8000/
```

### API Endpoints
- `POST /api/auth/verify-token/` - Magic Token tasdiqlash
- `GET /api/auth/profile/` - Profil ma'lumotlari
- `GET /api/auth/stadiums/` - Stadionlar ro'yxati
- `POST /api/auth/stadiums/` - Yangi stadion yaratish
- `GET /api/auth/stats/` - Foydalanuvchi statistikasi

## 🔒 Xavfsizlik

### Magic Token
- 10 daqiqa amal qiladi
- Bir marta ishlatiladi
- UUID format
- Avtomatik expire

### JWT Token
- Access token: 60 daqiqa
- Refresh token: 7 kun
- Blacklist qo'llab-quvvatlash

## 🚨 Xatoliklarni Hal Qilish

### Bot javob bermayapti
1. Bot token to'g'riligini tekshiring
2. Webhook/polling holatini tekshiring
3. Server loglarini ko'ring

### Magic Token ishlamayapti
1. Token muddati tugaganini tekshiring
2. Token ishlatilganini tekshiring
3. Database connection ni tekshiring

### Database xatoliklari
1. Migration qilganingizni tekshiring
2. Superuser yaratganingizni tekshiring
3. Model o'zgarishlarini tekshiring

## 📈 Kelajakdagi Rivojlantirish

- [ ] Real-time booking notifications
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Analytics dashboard
- [ ] Booking calendar
- [ ] Review system
- [ ] Geolocation features

## 🤝 Qo'llab-quvvatlash

Savollar yoki muammolar bo'lsa:
1. GitHub Issues yarating
2. Telegram: @support
3. Email: support@gobron.uz

---

**GoBron** - Futbol sevimchilar uchun qulay va zamonaviy bron qilish platformasi! ⚽🏟️