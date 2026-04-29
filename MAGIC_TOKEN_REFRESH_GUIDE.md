# 🔄 Magic Token Refresh System - Complete Guide

## ✅ Muammo Hal Qilindi!

### 🎯 Asosiy O'zgarishlar

1. **Token Muddati Uzaytirildi**: 10 daqiqadan → **7 kun**
2. **Ko'p Marta Ishlatish**: Token 10 marta ishlatilishi mumkin
3. **Avtomatik Yangilash**: Har `/start` da yangi token yaratiladi
4. **Aqlli Xatolik Xabarlari**: Aniq sabab ko'rsatiladi

## 🔧 Yangi MagicToken Model

### Yangi Maydonlar
```python
class MagicToken(models.Model):
    # Eski maydonlar
    user = models.ForeignKey(CustomUser, ...)
    token = models.UUIDField(...)
    created_at = models.DateTimeField(...)
    expires_at = models.DateTimeField(...)  # 7 kun
    
    # Yangi maydonlar
    usage_count = models.IntegerField(default=0)      # Necha marta ishlatilgan
    max_usage = models.IntegerField(default=10)       # Maksimal 10 marta
    
    # is_used maydoni o'chirildi
```

### Yangi Methodlar
```python
@property
def is_valid(self):
    return not self.is_expired and self.usage_count < self.max_usage

def use_token(self):
    """Tokenni ishlatish (usage_count ni oshirish)"""
    if self.is_valid:
        self.usage_count += 1
        self.save()
        return True
    return False

@classmethod
def create_or_refresh_token(cls, user):
    """Yangi token yaratish (eskisini o'chirish)"""
    # Eski faol tokenlarni o'chirish
    cls.objects.filter(user=user, expires_at__gt=timezone.now()).delete()
    
    # Yangi token yaratish
    return cls.objects.create(user=user)
```

## 🤖 Bot Flow Yangilandi

### Silent Auth (Mavjud Foydalanuvchi)
```
/start → Foydalanuvchi topildi → Eski tokenlar o'chirildi → Yangi token yaratildi → Link yuborildi
```

**Xabar:**
```
👋 Qaytib kelganingiz bilan, Kamol Mirzaboyev!

🎯 Sizning rolingiz: Futbolchi
📱 Ilovangiz: 🎮 Web Ilova

Maydonlarni ko'rish va bron qilish uchun

🔄 Yangi kirish linki yaratildi

[🎮 Ilovani ochish]
```

### Yangi Foydalanuvchi
```
/start → Rol tanlash → Telefon → Ism → Yangi token → Link
```

## 🌐 API Response Yangilandi

### Muvaffaqiyatli Response
```json
{
  "success": true,
  "message": "Muvaffaqiyatli autentifikatsiya",
  "user": {
    "id": 1,
    "phone_number": "+998901234567",
    "full_name": "Kamol Mirzaboyev",
    "user_role": "PLAYER",
    "telegram_id": 123456789,
    "is_phone_verified": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs..."
  },
  "token_info": {
    "usage_count": 1,
    "max_usage": 10,
    "expires_at": "2026-05-06T01:26:16.350720+00:00",
    "remaining_uses": 9
  },
  "redirect": true
}
```

### Xatolik Response (Muddati Tugagan)
```json
{
  "error": "Token muddati tugagan. Botdan yangi link oling.",
  "redirect": false,
  "expired": true
}
```

### Xatolik Response (Limit Tugagan)
```json
{
  "error": "Token ishlatish limiti tugagan. Botdan yangi link oling.",
  "redirect": false,
  "expired": true
}
```

## 📊 Admin Panel Yangilandi

### Magic Token List
- **Usage Count**: `1/10` format
- **Status**: Faol (1/10), Muddati tugagan, Limit tugagan
- **Expires At**: 7 kun keyingi sana
- **Usage Info**: Qancha marta ishlatilgan

### Filter Options
- Usage count bo'yicha
- Expires date bo'yicha
- Created date bo'yicha

## 🧪 Test Scenariyalari

### 1. **Yangi Token Yaratish**
```bash
# Bot orqali
@GoBronBot → /start → Yangi link olish

# Manual test
python3 -c "
from apps.accounts.models import *
user = CustomUser.objects.first()
token = MagicToken.create_or_refresh_token(user)
print(f'Token: {token.token}')
"
```

### 2. **Token Ko'p Marta Ishlatish**
```bash
# Bir xil tokenni 10 marta ishlatish
for i in {1..10}; do
  curl "http://localhost:8000/api/auth/web-auth/?token=YOUR_TOKEN"
done

# 11-chi marta xatolik beradi
```

### 3. **Token Muddati**
```python
# Token 7 kun amal qiladi
from datetime import timedelta
from django.utils import timezone

token = MagicToken.objects.first()
print(f"Yaratilgan: {token.created_at}")
print(f"Tugaydi: {token.expires_at}")
print(f"Qolgan vaqt: {token.expires_at - timezone.now()}")
```

## 🔄 Migration

Yangi maydonlar uchun migration bajarildi:
```bash
python3 manage.py makemigrations accounts
python3 manage.py migrate
```

**Migration fayli**: `0004_magictoken_max_usage_magictoken_usage_count.py`

## 🎯 Sayt Integration

### JavaScript Example (Yangilangan)
```javascript
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (token) {
    fetch(`/api/auth/web-auth/?token=${token}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // JWT tokenlarni saqlash
                localStorage.setItem('access_token', data.tokens.access);
                localStorage.setItem('refresh_token', data.tokens.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Token info saqlash
                localStorage.setItem('token_info', JSON.stringify(data.token_info));
                
                // Dashboard ga yo'naltirish
                redirectToDashboard(data.user.user_role);
            } else {
                // Xatolik ko'rsatish
                if (data.expired) {
                    showError('Token muddati tugagan. Botdan yangi link oling.');
                    // Bot linkini ko'rsatish
                    showBotLink();
                } else {
                    showError(data.error);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Server bilan bog\'lanishda xatolik');
        });
}

function showBotLink() {
    const botLink = document.createElement('a');
    botLink.href = 'https://t.me/GoBronBot';
    botLink.textContent = 'Botdan yangi link olish';
    botLink.target = '_blank';
    document.body.appendChild(botLink);
}
```

## 📈 Statistika

### Token Usage Tracking
```python
# Foydalanuvchi uchun token statistikasi
user = CustomUser.objects.get(phone_number='+998901234567')
tokens = MagicToken.objects.filter(user=user)

print(f"Jami tokenlar: {tokens.count()}")
print(f"Faol tokenlar: {tokens.filter(expires_at__gt=timezone.now()).count()}")
print(f"Ishlatilgan tokenlar: {tokens.filter(usage_count__gt=0).count()}")
```

## 🎉 Natija

### ✅ Hal Qilingan Muammolar
1. **Eski Token Muammosi**: Har `/start` da yangi token
2. **Qisqa Muddat**: 7 kun amal qilish
3. **Bir Marta Ishlatish**: 10 marta ishlatish imkoniyati
4. **Noaniq Xatoliklar**: Aniq sabab ko'rsatish

### 🚀 Yangi Imkoniyatlar
1. **Token Tracking**: Qancha marta ishlatilgan
2. **Flexible Usage**: Ko'p marta kirish
3. **Better UX**: Aniq xatolik xabarlari
4. **Admin Monitoring**: To'liq statistika

### 📱 Foydalanuvchi Tajribasi
- **Bot**: Har doim yangi link
- **Sayt**: 10 marta kirish mumkin
- **Xatolik**: Aniq yo'riqnoma
- **Monitoring**: Admin panelda to'liq ma'lumot

---

**Status**: 🟢 **TAYYOR VA ISHLAMOQDA**  
**Token Muddat**: 7 kun  
**Maksimal Ishlatish**: 10 marta  
**Auto Refresh**: ✅ Har `/start` da