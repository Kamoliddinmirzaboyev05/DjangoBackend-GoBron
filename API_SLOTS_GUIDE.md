# Slotlar bilan ishlash bo'yicha qo'llanma

## Umumiy ma'lumot

Slot tizimi 3 asosiy parametr bilan ishlaydi:

- **field_id** - Maydon identifikatori
- **slot_id** - Slot identifikatori  
- **date** - Sana (YYYY-MM-DD formatida)

**MUHIM:** Barcha slot API'lari **autentifikatsiya talab qilmaydi** (ochiq API).

## API Endpointlar

### 1. Maydon uchun mavjud sanalarni olish

```http
GET /api/fields/{field_id}/available-dates/
```

**Auth:** Talab qilinmaydi ❌

**Response:**

```json
{
  "field_id": 1,
  "field_name": "Chilonzor Stadium",
  "advance_booking_days": 7,
  "available_dates": [
    "2025-04-26",
    "2025-04-27",
    "2025-04-28",
    "2025-04-29",
    "2025-04-30",
    "2025-05-01",
    "2025-05-02"
  ]
}
```

### 2. Muayyan sana uchun slotlarni olish

```http
GET /api/fields/{field_id}/slots/?date=2025-04-26
```

**Auth:** Talab qilinmaydi ❌

**Query Parameters:**

- `date` (majburiy) - YYYY-MM-DD formatida sana

**Response:**

```json
{
  "field_id": 1,
  "field_name": "Chilonzor Stadium",
  "date": "2025-04-26",
  "price_per_hour": "150000.00",
  "advance_booking_days": 7,
  "available_dates": ["2025-04-26", "2025-04-27", "..."],
  "slots": [
    {
      "id": 123,
      "field": 1,
      "field_id": 1,
      "field_name": "Chilonzor Stadium",
      "date": "2025-04-26",
      "start_time": "08:00:00",
      "end_time": "09:00:00",
      "is_active": true,
      "is_booked": false
    },
    {
      "id": 124,
      "field": 1,
      "field_id": 1,
      "field_name": "Chilonzor Stadium",
      "date": "2025-04-26",
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "is_active": true,
      "is_booked": true
    }
  ]
}
```

### 3. Bitta slotni ID orqali olish

```http
GET /api/fields/slots/{slot_id}/
```

**Auth:** Talab qilinmaydi ❌

**Response:**

```json
{
  "slot": {
    "id": 123,
    "field": 1,
    "field_id": 1,
    "field_name": "Chilonzor Stadium",
    "date": "2025-04-26",
    "start_time": "08:00:00",
    "end_time": "09:00:00",
    "is_active": true,
    "is_booked": false
  },
  "field_id": 1,
  "field_name": "Chilonzor Stadium",
  "date": "2025-04-26",
  "price_per_hour": "150000.00"
}
```

### 4. Bron yaratish

```http
POST /api/bookings/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Auth:** Talab qilinadi ✅

#### Variant 1: Minimal (faqat slot_id)

```json
{
  "slot_id": 123,
  "note": "Ixtiyoriy izoh"
}
```

#### Variant 2: Qo'shimcha validatsiya bilan (tavsiya etiladi)

```json
{
  "slot_id": 123,
  "field_id": 1,
  "date": "2025-04-26",
  "note": "Ixtiyoriy izoh"
}
```

**Response:**

```json
{
  "id": 45,
  "field": 1,
  "field_detail": {
    "id": 1,
    "name": "Chilonzor Stadium",
    "city": "Toshkent"
  },
  "slot": 123,
  "user": 5,
  "date": "2025-04-26",
  "start_time": "08:00:00",
  "end_time": "09:00:00",
  "status": "pending",
  "status_display": "Kutilmoqda",
  "total_price": "150000.00",
  "booking_type": "online",
  "created_at": "2025-04-26T10:30:00Z"
}
```

## Ishlash tartibi (Frontend uchun)

### Oddiy oqim

1. **Maydonlar ro'yxatini ko'rsatish**

   ```http
   GET /api/fields/
   ```

2. **Maydon tanlanganda - mavjud sanalarni olish**

   ```http
   GET /api/fields/1/available-dates/
   ```

3. **Sana tanlanganda - o'sha kun uchun slotlarni olish**

   ```http
   GET /api/fields/1/slots/?date=2025-04-26
   ```

4. **Slot tanlanganda - bron yaratish**

   ```http
   POST /api/bookings/
   ```

   ```json
   {
     "slot_id": 123,
     "field_id": 1,
     "date": "2025-04-26"
   }
   ```

### Qo'shimcha validatsiya

Agar `field_id` va `date` parametrlari yuborilsa, backend quyidagilarni tekshiradi:

- Slot haqiqatan ham ko'rsatilgan maydonga tegishli ekanligini
- Slot haqiqatan ham ko'rsatilgan sanada ekanligini

Agar mos kelmasa, xato qaytariladi:

```json
{
  "field_id": ["Bu slot maydon #2 ga tegishli, lekin siz #1 ni ko'rsatdingiz."]
}
```

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
  "slot_id": ["Bu slot admin tomonidan o'chirilgan."]
}
```

### O'tgan vaqt

```json
{
  "slot_id": ["O'tgan vaqtga bron qilib bo'lmaydi."]
}
```

### Sana ruxsat etilmagan

```json
{
  "detail": "Bu maydon faqat 7 kun oldindan bron qilishga ruxsat beradi."
}
```

### Obuna tugagan

```json
{
  "non_field_errors": ["Bu maydonning obunasi tugagan."]
}
```

## Muhim eslatmalar

1. **Auth talab qilinmaydi** - Barcha slot API'lari (available-dates, slots, slot-detail) ochiq va autentifikatsiya talab qilmaydi. Faqat bron yaratish uchun auth kerak.

2. **Stadion ID qo'shildi** - Har bir slot ma'lumotida endi `field_id` va `field_name` ham qaytariladi, bu frontend uchun qulayroq.

3. **date parametri majburiy** - `/api/fields/{id}/slots/` endpointida `date` parametri majburiy. Agar berilmasa, 400 xato qaytariladi.

4. **Slot avtomatik generatsiya** - Agar berilgan sana uchun slotlar mavjud bo'lmasa, ular avtomatik yaratiladi.

5. **Slot band qilish** - Bron yaratilganda slot avtomatik `is_booked=True` qilinadi.

6. **Bron bekor qilish** - Faqat `pending` holatdagi bronlarni bekor qilish mumkin. Bekor qilinganda slot yana bo'sh bo'ladi.

7. **Advance booking** - Har bir maydon `advance_booking_days` parametriga ega. Bu foydalanuvchi necha kun oldindan bron qilishi mumkinligini belgilaydi.
