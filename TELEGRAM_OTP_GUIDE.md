# Telegram Bot OTP Integratsiyasi

Bu loyihada Telegram bot orqali OTP (One-Time Password) yuborish va telefon raqami bilan ro'yxatdan o'tish tizimi qo'shilgan.

## 🚀 Xususiyatlar

- ✅ Telefon raqami bilan ro'yxatdan o'tish
- ✅ Telegram bot orqali 4 xonali OTP yuborish
- ✅ OTP ni Redis/Cache da saqlash (5 daqiqa)
- ✅ Telefon raqami bilan kirish
- ✅ Telegram webhook qo'llab-quvvatlash
- ✅ Foydalanuvchi chat_id ni avtomatik saqlash

## 📋 Kerakli paketlar

```bash
pip install requests redis
```

## ⚙️ Sozlash

### 1. .env fayliga qo'shing:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo

# Redis (OTP uchun)
REDIS_URL=redis://localhost:6379/0
```

### 2. Redis o'rnatish (macOS):

```bash
brew install redis
brew services start redis
```

### 3. Migration qilish:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

## 🤖 Telegram Bot sozlash

### 1. Bot ishga tushirish (polling):

```bash
python manage.py telegram_bot
```

### 2. Webhook o'rnatish:

```bash
python manage.py telegram_bot --webhook
```

## 📱 API Endpoints

### Telefon raqami bilan ro'yxatdan o'tish

#### 1-qadam: OTP so'rash
```http
POST /api/auth/phone/register/
Content-Type: application/json

{
    "phone": "+998901234567",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
}
```

**Response:**
```json
{
    "message": "OTP kod Telegram orqali yuborildi",
    "phone": "+998901234567",
    "expires_in": 300
}
```

#### 2-qadam: OTP tasdiqlash va ro'yxatdan o'tish
```http
POST /api/auth/phone/verify-otp/
Content-Type: application/json

{
    "phone": "+998901234567",
    "otp": "1234",
    "password": "strong_password123",
    "password2": "strong_password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
}
```

**Response:**
```json
{
    "message": "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi",
    "user": {
        "id": 1,
        "phone": "+998901234567",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
        "is_phone_verified": true
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Telefon raqami bilan kirish

#### 1-qadam: OTP so'rash
```http
POST /api/auth/phone/login/
Content-Type: application/json

{
    "phone": "+998901234567"
}
```

#### 2-qadam: OTP tasdiqlash va kirish
```http
POST /api/auth/phone/verify-login/
Content-Type: application/json

{
    "phone": "+998901234567",
    "otp": "1234"
}
```

## 🔧 Telegram Bot buyruqlari

- `/start` - Botni ishga tushirish va telefon raqamini ulash
- `/help` - Yordam ma'lumotlari

## 📊 Model o'zgarishlari

### CustomUser modeli:
- `phone` - Telefon raqami (unique, required)
- `is_phone_verified` - Telefon tasdiqlangan
- `telegram_chat_id` - Telegram chat ID
- `USERNAME_FIELD = 'phone'` - Telefon bilan login

### PhoneVerification modeli:
- OTP kodlarni saqlash uchun
- Muddati tugagan kodlarni tekshirish

## 🔐 Xavfsizlik

- OTP kodlar 5 daqiqa amal qiladi
- Redis/Cache da xavfsiz saqlash
- Telefon raqami formatlash va validatsiya
- JWT token bilan autentifikatsiya

## 🚨 Muhim eslatmalar

1. **Telegram bot token** ni xavfsiz saqlang
2. **Redis** ishlab turganiga ishonch hosil qiling
3. Foydalanuvchi avval botga `/start` yozishi kerak
4. Telefon raqamini bot bilan ulash kerak
5. Production da webhook ishlatish tavsiya etiladi

## 🔄 Eski API bilan moslashuv

Eski username bilan ro'yxatdan o'tish va kirish API lari saqlanib qolgan:
- `POST /api/auth/register/`
- `POST /api/auth/login/`

## 🛠️ Muammolarni hal qilish

### OTP kelmayapti:
1. Bot token to'g'riligini tekshiring
2. Foydalanuvchi botga `/start` yozganini tekshiring
3. Telefon raqami to'g'ri formatda ekanini tekshiring
4. Redis ishlab turganini tekshiring

### Chat ID topilmayapti:
1. Foydalanuvchi botga telefon raqamini yuborishi kerak
2. `/start` buyrug'ini ishlatish kerak
3. Telefon raqami formati: +998XXXXXXXXX

## 📞 Qo'llab-quvvatlash

Muammolar yuzaga kelsa:
1. Loglarni tekshiring
2. Redis connection ni tekshiring
3. Telegram bot API javoblarini tekshiring
4. Phone format validatsiyasini tekshiring