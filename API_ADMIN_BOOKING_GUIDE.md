# Admin - Bron qilish qo'llanmasi

## Umumiy ma'lumot

Admin o'zi mijozlar uchun bron yaratishi mumkin. Admin tomonidan yaratilgan bronlar avtomatik ravishda **tasdiqlangan** holatda bo'ladi va tasdiqlanish talab qilinmaydi.

## Admin bron yaratish endpointi

```http
POST /api/admin/bookings/manual/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Auth:** Talab qilinadi ✅ (Admin role)

## Request Body

### Minimal (majburiy maydonlar)

```json
{
  "slot_id": 123,
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567"
}
```

### To'liq (barcha maydonlar bilan)

```json
{
  "field_id": 1,
  "slot_id": 123,
  "date": "2026-04-28",
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567",
  "plan": 150000.00,
  "note": "VIP mijoz, maxsus chegirma"
}
```

## Maydonlar tushuntirish

| Maydon | Turi | Majburiy | Tavsif |
|--------|------|----------|--------|
| `slot_id` | integer | ✅ Ha | Slot ID raqami |
| `guest_full_name` | string | ✅ Ha | Mijoz to'liq ismi |
| `guest_phone` | string | ✅ Ha | Mijoz telefon raqami |
| `field_id` | integer | ❌ Yo'q | Maydon ID (tekshirish uchun) |
| `date` | string (YYYY-MM-DD) | ❌ Yo'q | Sana (tekshirish uchun) |
| `plan` | decimal | ❌ Yo'q | To'lov summasi (ixtiyoriy) |
| `note` | string | ❌ Yo'q | Qo'shimcha izoh |

### `plan` maydoni haqida

- **Berilmasa**: Avtomatik hisoblash (maydon narxi × soat)
- **0 yoki 0.00**: Tekin o'yin
- **Boshqa qiymat**: Maxsus narx (chegirma, VIP, va h.k.)

## Response

```json
{
  "id": 45,
  "field": 1,
  "field_name": "Chilonzor Stadium",
  "field_city": "Toshkent",
  "user": null,
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567",
  "booking_type": "manual",
  "booking_type_display": "Qo'lda (admin)",
  "client_name": "Alisher Valiyev",
  "client_phone": "+998901234567",
  "date": "2026-04-28",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "status": "confirmed",
  "status_display": "Tasdiqlangan",
  "total_price": "150000.00",
  "note": "VIP mijoz, maxsus chegirma",
  "created_at": "2026-04-28T10:30:00Z",
  "confirmed_at": "2026-04-28T10:30:00Z"
}
```

## Ishlash tartibi

### 1. Slot tanlash

Avval maydon va sana uchun slotlarni oling:

```http
GET /api/fields/1/slots/?date=2026-04-28
```

Bo'sh slotni toping (`is_booked: false`).

### 2. Bron yaratish

#### Oddiy bron (avtomatik narx)

```json
{
  "slot_id": 123,
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567"
}
```

Narx avtomatik hisoblanadi: `maydon_narxi × soat`

#### Tekin o'yin

```json
{
  "slot_id": 123,
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567",
  "plan": 0,
  "note": "Tanlov g'olibi - tekin o'yin"
}
```

#### Maxsus narx (chegirma)

```json
{
  "slot_id": 123,
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567",
  "plan": 100000,
  "note": "Doimiy mijoz - 50% chegirma"
}
```

#### Qo'shimcha validatsiya bilan

```json
{
  "field_id": 1,
  "slot_id": 123,
  "date": "2026-04-28",
  "guest_full_name": "Alisher Valiyev",
  "guest_phone": "+998901234567",
  "plan": 150000
}
```

Agar `field_id` yoki `date` slot bilan mos kelmasa, xato qaytariladi.

## Xatolar

### Slot allaqachon band

```json
{
  "slot_id": ["Bu slot allaqachon band."]
}
```

### Slot nofaol

```json
{
  "slot_id": ["Bu slot nofaol."]
}
```

### field_id mos kelmaydi

```json
{
  "field_id": ["Bu slot maydon #2 ga tegishli, lekin siz #1 ni ko'rsatdingiz."]
}
```

### date mos kelmaydi

```json
{
  "date": ["Bu slot 2026-04-29 sanasiga tegishli, lekin siz 2026-04-28 ni ko'rsatdingiz."]
}
```

## Foydalanuvchi vs Admin bron

| Xususiyat | Foydalanuvchi | Admin |
|-----------|---------------|-------|
| Endpoint | `/api/bookings/` | `/api/admin/bookings/manual/` |
| Auth | User token | Admin token |
| Status | `pending` | `confirmed` |
| Tasdiqlanish | Kerak | Kerak emas |
| Mijoz ma'lumoti | Avtomatik (user) | Qo'lda kiritish |
| Narx | Avtomatik | Ixtiyoriy (plan) |
| Tekin o'yin | Yo'q | Ha (plan=0) |

## Muhim eslatmalar

1. **Avtomatik tasdiqlash** - Admin yaratgan bronlar darhol `confirmed` holatida bo'ladi

2. **Slot band qilish** - Bron yaratilishi bilan slot avtomatik `is_booked=true` bo'ladi

3. **plan maydoni** - Ixtiyoriy, lekin juda foydali:
   - Tekin o'yinlar uchun: `plan: 0`
   - Chegirmalar uchun: `plan: 100000` (50% chegirma)
   - VIP narxlar uchun: `plan: 300000`
   - Berilmasa: avtomatik hisoblash

4. **Validatsiya** - `field_id` va `date` ixtiyoriy, lekin qo'shilsa qo'shimcha tekshirish bo'ladi

5. **Bildirishnoma yo'q** - Admin yaratgan bronlar uchun foydalanuvchiga bildirishnoma yuborilmaydi

## Misollar

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/admin/bookings/manual/"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "Content-Type": "application/json"
}
data = {
    "slot_id": 123,
    "guest_full_name": "Alisher Valiyev",
    "guest_phone": "+998901234567",
    "plan": 150000,
    "note": "VIP mijoz"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### JavaScript (fetch)

```javascript
const url = 'http://localhost:8000/api/admin/bookings/manual/';
const data = {
  slot_id: 123,
  guest_full_name: 'Alisher Valiyev',
  guest_phone: '+998901234567',
  plan: 150000,
  note: 'VIP mijoz'
};

fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(booking => console.log('Bron yaratildi:', booking))
  .catch(error => console.error('Xato:', error));
```

### cURL

```bash
curl -X POST http://localhost:8000/api/admin/bookings/manual/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "slot_id": 123,
    "guest_full_name": "Alisher Valiyev",
    "guest_phone": "+998901234567",
    "plan": 150000,
    "note": "VIP mijoz"
  }'
```

## Boshqa admin endpointlar

### Bronlar ro'yxati

```http
GET /api/admin/bookings/
```

Filter: `?status=confirmed&date=2026-04-28&field=1`

### Bronni tasdiqlash

```http
PATCH /api/admin/bookings/{id}/confirm/
```

Faqat `pending` holatdagi bronlar uchun.

### Bronni rad etish

```http
PATCH /api/admin/bookings/{id}/reject/
```

`pending` yoki `confirmed` holatdagi bronlar uchun.

## Tez-tez beriladigan savollar

### Q: Admin o'zi uchun bron qila oladimi?

A: Ha, lekin `guest_full_name` va `guest_phone` ni kiritish kerak.

### Q: Tekin o'yinni qanday yaratish mumkin?

A: `plan: 0` yoki `plan: 0.00` qilib yuboring.

### Q: Narxni qanday o'zgartirish mumkin?

A: `plan` maydoniga kerakli summani kiriting. Misol: `plan: 100000`

### Q: Agar plan berilmasa nima bo'ladi?

A: Narx avtomatik hisoblanadi: `maydon_narxi × soat`

### Q: Admin yaratgan bronni tasdiqlanish kerakmi?

A: Yo'q, avtomatik `confirmed` holatida yaratiladi.
