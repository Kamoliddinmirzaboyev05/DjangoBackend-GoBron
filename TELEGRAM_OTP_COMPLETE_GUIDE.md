# 🤖 GoBron Telegram Bot - OTP Authentication Guide

## 📋 Umumiy Ma'lumot

GoBron Telegram Bot endi **OTP (One-Time Password)** autentifikatsiya tizimi bilan ishlaydi. Foydalanuvchilar telefon raqamlarini tasdiqlash uchun 4 xonali kod olishadi.

## 🔄 Yangi Authentication Flow

### 1. **Silent Auth** (Mavjud Foydalanuvchilar)
```
/start → Foydalanuvchi topildi → Magic Link yuborish
```

### 2. **OTP Registration** (Yangi Foydalanuvchilar)
```
/start → Rol tanlash → Telefon yuborish → Ism kiriting → OTP kod → Tasdiqlash → Magic Link
```

## 🛠️ Texnik Tafsilotlar

### OTP Model
```python
class OTPCode(models.Model):
    phone_number = models.CharField(max_length=20)
    telegram_id = models.BigIntegerField()
    code = models.CharField(max_length=4)  # 4 xonali tasodifiy kod
    user_role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    telegram_username = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)  # Maksimal 3 ta urinish
    expires_at = models.DateTimeField()  # 5 daqiqa amal qiladi
```

### Bot States
```python
class RegistrationStates(StatesGroup):
    waiting_for_role = State()      # Rol tanlash
    waiting_for_contact = State()   # Telefon raqami
    waiting_for_name = State()      # Ism-familiya
    waiting_for_otp = State()       # OTP kod kutish
```

## 🎯 Bot Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish va autentifikatsiya |
| `/help` | Yordam va ko'rsatmalar |
| `/profile` | Foydalanuvchi profili |
| `/resend_otp` | OTP kodni qayta yuborish |

## 📱 Foydalanuvchi Tajribasi

### Yangi Foydalanuvchi Ro'yxatdan O'tishi

1. **Bot Boshlash**
   ```
   👋 GoBron platformasiga xush kelibsiz!
   
   Bu yerda siz:
   ⚽ Futbol maydonlarini topishingiz
   📅 Maydonlarni bron qilishingiz
   🏟️ O'z maydonlaringizni boshqarishingiz mumkin
   
   Davom etish uchun rolni tanlang:
   [⚽ Futbolchiman] [🏟️ Maydon egasiman]
   ```

2. **Rol Tanlash**
   ```
   ✅ Rol tanlandi: Futbolchi
   
   Endi telefon raqamingizni yuboring:
   [📱 Telefon raqamini yuborish]
   ```

3. **Ism Kiritish**
   ```
   📝 Ism-familiyangizni kiriting:
   
   Masalan: Akmal Karimov
   ```

4. **OTP Kod Olish**
   ```
   🔐 Tasdiqlash kodi:
   
   1234
   
   📱 Telefon raqamingiz: +998901234567
   ⏰ Kod 5 daqiqa amal qiladi
   
   Kodni quyidagi xabarga yozing:
   ```

5. **Muvaffaqiyatli Ro'yxatdan O'tish**
   ```
   🎉 Telefon raqami tasdiqlandi!
   
   ✅ Ro'yxatdan o'tish muvaffaqiyatli!
   
   👤 Ism: Akmal Karimov
   📱 Telefon: +998901234567
   ⚽ Rol: Futbolchi
   🎯 Ilovangiz: 🎮 Telegram Mini App
   
   Maydonlarni ko'rish va bron qilish uchun
   
   [🎮 Ilovani ochish]
   ```

### Mavjud Foydalanuvchi (Silent Auth)

```
👋 Salom, Akmal Karimov!

🎯 Sizning rolingiz: Futbolchi
📱 Ilovangiz: 🎮 Telegram Mini App

Maydonlarni ko'rish va bron qilish uchun

[🎮 Ilovani ochish]
```

## 🔧 Botni Ishga Tushirish

### 1. Bot Tokenini Sozlash
`.env` faylida:
```env
TELEGRAM_BOT_TOKEN=8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo
TELEGRAM_BOT_USERNAME=GoBronBot
```

### 2. Migratsiyalarni Bajarish
```bash
python3 manage.py makemigrations accounts
python3 manage.py migrate
```

### 3. Botni Ishga Tushirish
```bash
python3 manage.py run_bot
```

### 4. Debug Rejimida Ishga Tushirish
```bash
python3 manage.py run_bot --debug
```

## 🛡️ Xavfsizlik Choralari

### OTP Xavfsizligi
- **Kod uzunligi**: 4 xonali raqam (1000-9999)
- **Amal qilish muddati**: 5 daqiqa
- **Maksimal urinishlar**: 3 marta
- **Avtomatik o'chirish**: Eski kodlar yangi kod yaratilganda o'chiriladi

### Telefon Raqami Formatlash
```python
def format_phone_number(phone):
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    if clean_phone.startswith('998'):
        return f"+{clean_phone}"
    elif clean_phone.startswith('8') and len(clean_phone) == 9:
        return f"+99{clean_phone}"
    elif len(clean_phone) == 9:
        return f"+998{clean_phone}"
    else:
        return f"+{clean_phone}"
```

## 📊 Admin Panel

### OTP Kodlarni Boshqarish
Admin panelda `/admin/accounts/otpcode/` sahifasida:

- **Barcha OTP kodlar** ro'yxati
- **Holat ko'rsatkichlari**: Kutilmoqda, Tasdiqlangan, Muddati tugagan, Bloklangan
- **Filtrlash**: Rol, holat, sana bo'yicha
- **Qidiruv**: Telefon raqami, ism, Telegram ID bo'yicha

### Foydalanuvchi Statistikasi
```python
# OTP statistikasi
total_otps = OTPCode.objects.count()
verified_otps = OTPCode.objects.filter(is_verified=True).count()
expired_otps = OTPCode.objects.filter(is_expired=True).count()
blocked_otps = OTPCode.objects.filter(attempts__gte=3).count()
```

## 🧪 Test Qilish

### OTP Funksiyasini Test Qilish
```bash
python3 test_otp.py
```

Bu script quyidagilarni test qiladi:
- OTP kod yaratish
- Kod tekshirish
- Foydalanuvchi yaratish

### Manual Test
1. Telegram botiga `/start` yuboring
2. Rol tanlang
3. Telefon raqamini yuboring
4. Ismingizni kiriting
5. OTP kodni kiriting
6. Magic Link orqali ilovaga kiring

## 🔄 Xatoliklarni Bartaraf Etish

### Keng Tarqalgan Xatoliklar

1. **"Kod yaroqsiz yoki muddati tugagan"**
   - Yangi kod so'rang: `/resend_otp`
   - 5 daqiqadan ko'p vaqt o'tgan bo'lsa

2. **"Juda ko'p noto'g'ri urinish"**
   - Qaytadan boshlash: `/start`
   - 3 martadan ko'p noto'g'ri kod kiritilgan

3. **"Bot javob bermayapti"**
   - Bot ishga tushganligini tekshiring
   - Token to'g'riligini tekshiring
   - Log fayllarni ko'ring

### Log Monitoring
```bash
# Bot loglarini kuzatish
tail -f logs/bot.log

# Django loglarini kuzatish  
tail -f logs/django.log
```

## 🚀 Keyingi Qadamlar

1. **SMS Integration**: Haqiqiy SMS xizmati bilan integratsiya
2. **Rate Limiting**: OTP so'rashni cheklash
3. **Analytics**: OTP muvaffaqiyat statistikasi
4. **Backup Codes**: Zaxira autentifikatsiya usullari
5. **Multi-language**: Ko'p tilni qo'llab-quvvatlash

## 📞 Qo'llab-quvvatlash

Agar savollaringiz bo'lsa:
- **Telegram**: @support
- **Email**: support@gobron.uz
- **GitHub Issues**: Repository issues bo'limida

---

**Eslatma**: Bu guide GoBron v2.0 uchun mo'ljallangan va OTP autentifikatsiya tizimi bilan ishlaydi.