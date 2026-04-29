# 🌐 GoBron Web Integration Guide

## ✅ Bot va Sayt Integratsiyasi Muvaffaqiyatli!

### 🔗 Sayt URL
**https://gobron.webportfolio.uz**

### 🤖 Bot Flow (Yangilangan)

1. **Role Selection**: Futbolchi yoki Maydon egasi
2. **Contact Sharing**: Telefon raqamini yuborish
3. **Name Input**: Ism-familiya kiritish
4. **Direct Registration**: OTP siz to'g'ridan-to'g'ri ro'yxatdan o'tish
5. **Magic Link**: Saytga yo'naltiruvchi tugma

### 📱 Bot Test Scenariosi

```
/start
↓
[⚽ Futbolchiman] [🏟️ Maydon egasiman]
↓
[📱 Telefon raqamini yuborish]
↓
"Ism-familiyangizni kiriting:"
↓
"Kamol Mirzaboyev"
↓
🎉 Ro'yxatdan o'tish muvaffaqiyatli!
[🎮 Ilovani ochish] ← Bu tugma saytni ochadi
```

## 🔧 API Endpoints

### 1. **Web Authentication Endpoint**
```
GET /api/auth/web-auth/?token={MAGIC_TOKEN}
```

**Response (Success):**
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
  "redirect": true
}
```

**Response (Error):**
```json
{
  "error": "Token topilmadi",
  "redirect": false
}
```

### 2. **Magic Token Verification (POST)**
```
POST /api/auth/verify-token/
Content-Type: application/json

{
  "token": "154c7e6a-2763-4299-b9ed-fb94f5aef59c"
}
```

## 🎯 Sayt Integration

### JavaScript Example
```javascript
// URL dan token olish
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (token) {
    // Magic Token bilan autentifikatsiya
    fetch(`/api/auth/web-auth/?token=${token}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // JWT tokenlarni saqlash
                localStorage.setItem('access_token', data.tokens.access);
                localStorage.setItem('refresh_token', data.tokens.refresh);
                
                // Foydalanuvchi ma'lumotlarini saqlash
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Dashboard ga yo'naltirish
                if (data.user.user_role === 'PLAYER') {
                    window.location.href = '/player-dashboard';
                } else {
                    window.location.href = '/owner-dashboard';
                }
            } else {
                // Xatolik ko'rsatish
                alert('Autentifikatsiya xatosi: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Server xatosi');
        });
}
```

### React Example
```jsx
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function AuthHandler() {
    const [searchParams] = useSearchParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const token = searchParams.get('token');
        
        if (token) {
            authenticateWithToken(token);
        } else {
            setError('Token topilmadi');
            setLoading(false);
        }
    }, [searchParams]);
    
    const authenticateWithToken = async (token) => {
        try {
            const response = await fetch(`/api/auth/web-auth/?token=${token}`);
            const data = await response.json();
            
            if (data.success) {
                // JWT tokenlarni saqlash
                localStorage.setItem('access_token', data.tokens.access);
                localStorage.setItem('refresh_token', data.tokens.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Redirect based on role
                if (data.user.user_role === 'PLAYER') {
                    window.location.href = '/player-dashboard';
                } else {
                    window.location.href = '/owner-dashboard';
                }
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('Server bilan bog\'lanishda xatolik');
        } finally {
            setLoading(false);
        }
    };
    
    if (loading) return <div>Yuklanmoqda...</div>;
    if (error) return <div>Xatolik: {error}</div>;
    
    return <div>Autentifikatsiya muvaffaqiyatli!</div>;
}
```

## 🔒 CORS Sozlamalari

Sayt uchun CORS sozlangan:
```python
CORS_ALLOWED_ORIGINS = [
    "https://gobron.webportfolio.uz",
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://127.0.0.1:3000",
]
```

## 🧪 Test Qilish

### 1. **Bot orqali Magic Link olish**
1. `@GoBronBot` ga `/start` yuboring
2. Rolni tanlang
3. Telefon raqamingizni yuboring
4. Ismingizni kiriting
5. "🎮 Ilovani ochish" tugmasini bosing

### 2. **Manual API Test**
```bash
# Magic Token yaratish
python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.accounts.models import CustomUser, MagicToken
user = CustomUser.objects.first()
token = MagicToken.objects.create(user=user)
print(f'Test URL: https://gobron.webportfolio.uz?token={token.token}')
"

# API test qilish
curl "http://localhost:8000/api/auth/web-auth/?token=YOUR_TOKEN"
```

## 🎯 Sayt Funksiyalari

### Foydalanuvchi Rollari
- **PLAYER**: Maydonlarni ko'rish va bron qilish
- **OWNER**: Maydonlarni boshqarish va statistika

### JWT Token Usage
```javascript
// API so'rovlarda JWT token ishlatish
const token = localStorage.getItem('access_token');

fetch('/api/fields/', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🚀 Production Deployment

### Environment Variables
```env
# Backend
CORS_ALLOWED_ORIGINS=https://gobron.webportfolio.uz
TELEGRAM_BOT_TOKEN=8659084348:AAHi8Ds08Wtts22VebR-CI7Y5kQgtPAxhGo

# Frontend
REACT_APP_API_URL=https://api.gobron.uz
REACT_APP_BOT_URL=https://t.me/GoBronBot
```

### SSL Certificate
- Backend: `https://api.gobron.uz`
- Frontend: `https://gobron.webportfolio.uz`
- Bot Webhook: `https://api.gobron.uz/webhook/`

## 📞 Qo'llab-quvvatlash

Agar muammolar bo'lsa:
- **Telegram**: @support
- **GitHub**: Repository issues
- **API Docs**: `http://localhost:8000/` (Swagger UI)

---

**Status**: 🟢 **TAYYOR VA ISHLAMOQDA**  
**Sana**: 2026-04-29  
**Integration**: Bot ↔ API ↔ Web ✅