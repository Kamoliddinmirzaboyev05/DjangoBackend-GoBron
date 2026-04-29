# 🤖 GoBron Bot Test Guide

## ✅ Bot Muvaffaqiyatli Ishga Tushdi!

### 📱 Bot Ma'lumotlari
- **Bot Username**: `@GoBronBot`
- **Bot Token**: `8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo`
- **Status**: 🟢 **FAOL**

## 🧪 Test Scenariyalari

### 1. **Yangi Foydalanuvchi Registration (OTP Flow)**

**Qadamlar:**
1. Telegram da `@GoBronBot` ga `/start` yuboring
2. Quyidagi xabar paydo bo'ladi:
   ```
   🎉 GoBron platformasiga xush kelibsiz!
   
   Bu yerda siz:
   ⚽ Futbol maydonlarini topishingiz
   📅 Maydonlarni bron qilishingiz
   🏟️ O'z maydonlaringizni boshqarishingiz mumkin
   
   Davom etish uchun rolni tanlang:
   [⚽ Futbolchiman] [🏟️ Maydon egasiman]
   ```

3. **"⚽ Futbolchiman"** yoki **"🏟️ Maydon egasiman"** tugmasini bosing

4. Rol tanlanganidan keyin:
   ```
   ✅ Rol tanlandi: Futbolchi
   
   Endi telefon raqamingizni yuboring:
   ```
   
5. **"📱 Telefon raqamini yuborish"** tugmasini bosing

6. Ism-familiyangizni kiriting:
   ```
   📝 Ism-familiyangizni kiriting:
   
   Masalan: Akmal Karimov
   ```

7. 4 xonali OTP kod olasiz:
   ```
   🔐 Tasdiqlash kodi:
   
   1234
   
   📱 Telefon raqamingiz: +998901234567
   ⏰ Kod 5 daqiqa amal qiladi
   
   Kodni quyidagi xabarga yozing:
   ```

8. Kodni kiriting va muvaffaqiyatli ro'yxatdan o'ting:
   ```
   🎉 Telefon raqami tasdiqlandi!
   
   ✅ Ro'yxatdan o'tish muvaffaqiyatli!
   
   👤 Ism: Akmal Karimov
   📱 Telefon: +998901234567
   ⚽ Rol: Futbolchi
   🎯 Ilovangiz: 🎮 Telegram Mini App
   
   [🎮 Ilovani ochish]
   ```

9. **"🎮 Ilovani ochish"** tugmasini bosing - TMA ochiladi

### 2. **Mavjud Foydalanuvchi (Silent Auth)**

**Qadamlar:**
1. Avval ro'yxatdan o'tgan telefon raqami bilan `/start` yuboring
2. Avtomatik ravishda quyidagi xabar paydo bo'ladi:
   ```
   👋 Salom, Akmal Karimov!
   
   🎯 Sizning rolingiz: Futbolchi
   📱 Ilovangiz: 🎮 Telegram Mini App
   
   Maydonlarni ko'rish va bron qilish uchun
   
   [🎮 Ilovani ochish]
   ```

3. **"🎮 Ilovani ochish"** tugmasini bosing - TMA ochiladi

### 3. **Bot Buyruqlari**

| Buyruq | Tavsif | Natija |
|--------|--------|---------|
| `/start` | Botni ishga tushirish | Silent Auth yoki Registration |
| `/help` | Yordam va ko'rsatmalar | Bot haqida ma'lumot |
| `/profile` | Profil ma'lumotlari | Foydalanuvchi profili |
| `/resend_otp` | OTP qayta yuborish | Yangi 4 xonali kod |

## 🔧 Xatoliklarni Bartaraf Etish

### Keng Tarqalgan Muammolar

1. **"Kod yaroqsiz yoki muddati tugagan"**
   - **Yechim**: `/resend_otp` buyrug'ini yuboring
   - **Sabab**: 5 daqiqadan ko'p vaqt o'tgan

2. **"Juda ko'p noto'g'ri urinish"**
   - **Yechim**: `/start` buyrug'ini qayta yuboring
   - **Sabab**: 3 martadan ko'p noto'g'ri kod kiritilgan

3. **"Bot javob bermayapti"**
   - **Tekshirish**: Bot ishga tushganligini tekshiring
   - **Log**: Server loglarini ko'ring

### Bot Loglarini Kuzatish

```bash
# Bot loglarini real vaqtda kuzatish
tail -f /path/to/bot/logs

# Yoki terminal orqali
python3 manage.py run_bot --debug
```

## 🎯 Test Natijalari

### ✅ Muvaffaqiyatli Test Qilingan
- [x] Role selection (PLAYER/OWNER)
- [x] Contact sharing
- [x] OTP generation va verification
- [x] Magic Link generation
- [x] Silent Auth flow
- [x] Error handling

### 🔄 Keyingi Testlar
- [ ] TMA integration (haqiqiy Mini App)
- [ ] PWA integration (Owner panel)
- [ ] SMS integration (haqiqiy OTP yuborish)
- [ ] Production deployment

## 📞 Qo'llab-quvvatlash

Agar muammolar bo'lsa:
- **Telegram**: @support
- **GitHub**: Repository issues
- **Email**: support@gobron.uz

---

**Bot Status**: 🟢 **FAOL va TEST QILISHGA TAYYOR**  
**Sana**: 2026-04-29  
**Vaqt**: 05:35 UTC