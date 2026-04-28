# Telegram Bot O'rnatish va Sozlash

## 🤖 Bot yaratish

1. Telegram da @BotFather ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting: `Football Booking Bot`
4. Bot username kiriting: `football_booking_bot` (yoki boshqa)
5. Bot token ni oling: `8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo`

## ⚙️ Bot sozlash

### 1. Bot buyruqlarini o'rnatish

@BotFather ga `/setcommands` yuboring va quyidagi buyruqlarni kiriting:

```
start - Botni ishga tushirish
help - Yordam ma'lumotlari
```

### 2. Bot tavsifini o'rnatish

@BotFather ga `/setdescription` yuboring:

```
🏟️ Football Booking - Futbol maydonlarini bron qilish tizimi

Bu bot orqali siz:
• Telefon raqamingizni tasdiqlashingiz mumkin
• OTP kodlarini olishingiz mumkin
• Tizimga xavfsiz kirishingiz mumkin
```

### 3. Bot haqida qisqa ma'lumot

@BotFather ga `/setabouttext` yuboring:

```
Football Booking tizimi uchun OTP bot
```

## 🚀 Bot ishga tushirish

### Polling rejimida (development):

```bash
python manage.py telegram_bot
```

### Webhook rejimida (production):

1. Webhook URL ni o'rnating:
```bash
python manage.py telegram_bot --webhook
```

2. Yoki qo'lda o'rnating:
```bash
curl -X POST "https://api.telegram.org/bot8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/auth/telegram/webhook/"}'
```

## 📱 Foydalanuvchi uchun yo'riqnoma

### 1. Botni ishga tushirish
- Telegram da `@football_booking_bot` ni toping
- `/start` buyrug'ini yuboring
- "📱 Telefon raqamini yuborish" tugmasini bosing
- Telefon raqamingizni yuboring

### 2. Ro'yxatdan o'tish
1. Mobil ilovani oching
2. "Telefon raqami bilan ro'yxatdan o'tish" ni tanlang
3. Telefon raqamingizni kiriting
4. Bot sizga 4 xonali OTP kod yuboradi
5. Kodni ilovaga kiriting
6. Parol o'rnating va ro'yxatdan o'ting

### 3. Kirish
1. Mobil ilovada "Telefon raqami bilan kirish" ni tanlang
2. Telefon raqamingizni kiriting
3. Bot sizga yangi OTP kod yuboradi
4. Kodni ilovaga kiriting

## 🔧 Texnik ma'lumotlar

### Bot API endpoints:
- **Webhook URL**: `/api/auth/telegram/webhook/`
- **Bot Token**: `8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo`

### Bot buyruqlari:
- `/start` - Botni ishga tushirish va telefon raqamini ulash
- `/help` - Yordam ma'lumotlari

### Xabar formatlari:
- OTP xabarlari HTML formatda yuboriladi
- Emoji va formatting ishlatiladi
- Kod `<code>` tag bilan ajratiladi

## 🛠️ Muammolarni hal qilish

### Bot javob bermayapti:
1. Bot token to'g'riligini tekshiring
2. Webhook URL ni tekshiring
3. Server loglarini ko'ring

### OTP kelmayapti:
1. Foydalanuvchi botga `/start` yozganini tekshiring
2. Telefon raqami bot bilan ulanganini tekshiring
3. Chat ID saqlangan ekanini tekshiring

### Webhook ishlamayapti:
1. HTTPS ishlatilganini tekshiring
2. SSL sertifikat yaroqli ekanini tekshiring
3. Webhook URL ga POST so'rov yuborilishini tekshiring

## 📊 Monitoring

### Bot statistikasi:
```bash
curl "https://api.telegram.org/bot8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo/getMe"
```

### Webhook ma'lumotlari:
```bash
curl "https://api.telegram.org/bot8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo/getWebhookInfo"
```

### Webhook o'chirish:
```bash
curl -X POST "https://api.telegram.org/bot8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo/deleteWebhook"
```