# Swagger UI da Autentifikatsiya qilish

## Qadamma-qadam qo'llanma

### 1. Swagger UI ni oching

Brauzerda quyidagi manzilni oching:

```
http://localhost:8000/api/schema/swagger-ui/
```

### 2. Login qiling va token oling

1. **Auth** bo'limini oching
2. **POST /api/auth/login/** endpointini toping
3. **"Try it out"** tugmasini bosing
4. Request body ga username va password kiriting:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

5. **"Execute"** tugmasini bosing
6. Response dan `access` tokenni nusxalang:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0MjE4MDAwLCJpYXQiOjE3MTQyMTQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.abcdefghijklmnopqrstuvwxyz",
  "refresh": "...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### 3. Authorize tugmasini bosing

Sahifaning yuqori o'ng tomonida **"Authorize"** 🔓 tugmasi bor. Uni bosing.

### 4. Tokenni kiriting

1. **BearerAuth (http, Bearer)** qismida input maydon paydo bo'ladi
2. Nusxalangan tokenni kiriting (faqat token, "Bearer" so'zisiz)
3. **"Authorize"** tugmasini bosing
4. **"Close"** tugmasini bosing

### 5. Tayyor!

Endi barcha autentifikatsiya talab qiladigan endpointlar ishlaydi. Token avtomatik ravishda har bir so'rovga qo'shiladi.

## Muhim eslatmalar

### ✅ To'g'ri

Faqat tokenni kiriting:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0MjE4MDAwLCJpYXQiOjE3MTQyMTQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.abcdefghijklmnopqrstuvwxyz
```

### ❌ Noto'g'ri

"Bearer" so'zini qo'shmaslik kerak:

```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Token muddati tugasa

Agar token muddati tugasa (default: 60 daqiqa), quyidagi xatoni olasiz:

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Yechim:** Yangi token oling:

1. **POST /api/auth/refresh/** endpointidan foydalaning (refresh token bilan)
2. Yoki qaytadan login qiling

## Refresh token bilan yangi access token olish

1. **POST /api/auth/refresh/** endpointini oching
2. **"Try it out"** tugmasini bosing
3. Request body ga refresh tokenni kiriting:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

4. **"Execute"** tugmasini bosing
5. Yangi `access` tokenni nusxalang va yuqoridagi qadamlarni takrorlang

## Logout qilish

1. **POST /api/auth/logout/** endpointini oching
2. **"Try it out"** tugmasini bosing
3. Request body ga refresh tokenni kiriting:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

4. **"Execute"** tugmasini bosing
5. Token blacklist ga qo'shiladi va endi ishlatib bo'lmaydi

## Swagger UI sozlamalari

Swagger UI da quyidagi sozlamalar yoqilgan:

- **persistAuthorization: true** - Token brauzer xotirasida saqlanadi (sahifani yangilasangiz ham)
- **deepLinking: true** - URL orqali to'g'ridan-to'g'ri endpointga o'tish mumkin
- **filter: true** - Endpointlarni qidirish mumkin

## Turli rollar uchun test foydalanuvchilar

### Admin

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Oddiy foydalanuvchi

```json
{
  "username": "user",
  "password": "user123"
}
```

## Maslahatlar

1. **Token nusxalashda** - Tokenning boshidan va oxiridan bo'sh joylar yo'qligiga ishonch hosil qiling
2. **Xavfsizlik** - Production muhitda tokenlarni console.log qilmang
3. **Token muddati** - `.env` faylida `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` ni o'zgartirish mumkin
4. **Refresh token** - Refresh token 7 kun amal qiladi (default)

## Tez-tez beriladigan savollar

### Q: Token qayerda saqlanadi?

A: Swagger UI tokenni brauzer localStorage da saqlaydi. Sahifani yangilasangiz ham token saqlanib qoladi.

### Q: Bir nechta tab ochsam ishlaydi?

A: Ha, token barcha tablarda ishlaydi (bir xil brauzerda).

### Q: Token xavfsizmi?

A: Swagger UI faqat development uchun. Production da frontend ilovasidan foydalaning.

### Q: Tokenni qanday o'chirish mumkin?

A: Authorize oynasini oching va **"Logout"** tugmasini bosing yoki brauzer localStorage ni tozalang.

## Muammolarni hal qilish

### Muammo: "Unauthorized" xatosi

**Yechim:**
1. Tokenni to'g'ri nusxalaganingizni tekshiring
2. Token muddati tugamaganligini tekshiring
3. Authorize tugmasini bosganingizni tekshiring

### Muammo: "Token is invalid or expired"

**Yechim:**
1. Yangi token oling (login yoki refresh)
2. Tokenni qayta kiriting

### Muammo: "Given token not valid for any token type"

**Yechim:**
1. Token formati to'g'ri ekanligini tekshiring
2. "Bearer" so'zini qo'shmaganingizni tekshiring
3. Tokenning boshidan va oxiridan bo'sh joylar yo'qligini tekshiring

## Qo'shimcha ma'lumot

Swagger UI hujjatlari: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/

DRF Spectacular hujjatlari: https://drf-spectacular.readthedocs.io/
