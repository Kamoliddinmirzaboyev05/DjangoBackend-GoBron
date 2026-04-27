# Admin - Maydonlar bilan ishlash bo'yicha qo'llanma

## Umumiy ma'lumot

Admin bir nechta maydonga ega bo'lishi mumkin. Har bir maydon uchun alohida rasm yuklash, tahrirlash va boshqarish imkoniyati mavjud.

## API Endpointlar

### 1. O'z maydonlarim ro'yxati

```http
GET /api/fields/my-fields/
Authorization: Bearer <access_token>
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Response:**

```json
[
  {
    "id": 1,
    "name": "Chilonzor Stadium",
    "description": "Katta futbol maydoni",
    "address": "Chilonzor tumani, 12-kvartal",
    "city": "Toshkent",
    "location_url": "https://maps.google.com/...",
    "phone": "+998901234567",
    "price_per_hour": "150000.00",
    "opening_time": "08:00:00",
    "closing_time": "23:00:00",
    "advance_booking_days": 7,
    "is_active": true,
    "subscription_valid": true,
    "cover_image": "/media/fields/covers/image.jpg",
    "cover_image_url": "http://localhost:8000/media/fields/covers/image.jpg",
    "images": [
      {
        "id": 1,
        "image_url": "http://localhost:8000/media/fields/images/img1.jpg",
        "order": 0
      },
      {
        "id": 2,
        "image_url": "http://localhost:8000/media/fields/images/img2.jpg",
        "order": 1
      }
    ],
    "amenities": [
      {
        "id": 1,
        "name": "Kiyinish xonasi",
        "icon": "🚿"
      }
    ],
    "created_at": "2025-04-20T10:00:00Z",
    "updated_at": "2025-04-25T15:30:00Z"
  },
  {
    "id": 2,
    "name": "Yunusobod Arena",
    "address": "Yunusobod tumani, 5-kvartal",
    "city": "Toshkent",
    "price_per_hour": "200000.00",
    "images": []
  }
]
```

### 2. Yangi maydon yaratish

```http
POST /api/fields/my-fields/create/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Request Body:**

```json
{
  "name": "Yangi Stadion",
  "description": "Zamonaviy futbol maydoni",
  "address": "Sergeli tumani, 10-kvartal",
  "city": "Toshkent",
  "location_url": "https://maps.google.com/...",
  "phone": "+998901234567",
  "price_per_hour": "180000.00",
  "opening_time": "08:00:00",
  "closing_time": "23:00:00",
  "advance_booking_days": 7,
  "is_active": true,
  "subscription_start": "2025-04-27",
  "subscription_end": "2025-05-27",
  "is_subscription_active": true
}
```

**Response:**

```json
{
  "id": 3,
  "name": "Yangi Stadion",
  "description": "Zamonaviy futbol maydoni",
  "address": "Sergeli tumani, 10-kvartal",
  "city": "Toshkent",
  "location_url": "https://maps.google.com/...",
  "phone": "+998901234567",
  "price_per_hour": "180000.00",
  "opening_time": "08:00:00",
  "closing_time": "23:00:00",
  "advance_booking_days": 7,
  "is_active": true,
  "subscription_valid": true,
  "images": [],
  "amenities": [],
  "created_at": "2025-04-27T10:00:00Z"
}
```

### 3. Maydon tafsilotlari

```http
GET /api/fields/my-fields/{field_id}/
Authorization: Bearer <access_token>
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Response:** Yuqoridagi ro'yxatdagi bitta maydon ma'lumoti

### 4. Maydonni tahrirlash

```http
PATCH /api/fields/my-fields/{field_id}/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Request Body (partial update):**

```json
{
  "name": "Yangilangan nom",
  "price_per_hour": "200000.00",
  "opening_time": "07:00:00"
}
```

**Response:** Yangilangan maydon ma'lumoti

### 5. Maydonga rasm yuklash

```http
POST /api/fields/my-fields/upload-images/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Form Data:**

- `field_id` (majburiy) - Maydon ID raqami
- `images` (majburiy) - Bir yoki bir nechta rasm fayllari

**cURL misoli:**

```bash
curl -X POST http://localhost:8000/api/fields/my-fields/upload-images/ \
  -H "Authorization: Bearer <access_token>" \
  -F "field_id=1" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

**Response:**

```json
[
  {
    "id": 10,
    "image_url": "http://localhost:8000/media/fields/images/image1.jpg",
    "order": 0
  },
  {
    "id": 11,
    "image_url": "http://localhost:8000/media/fields/images/image2.jpg",
    "order": 0
  }
]
```

**Muhim:** Yuklangan rasmlar mavjud rasmlar ro'yxatiga qo'shiladi (eski rasmlar o'chirilmaydi).

### 6. Rasmni o'chirish

```http
DELETE /api/fields/images/{image_id}/
Authorization: Bearer <access_token>
```

**Auth:** Talab qilinadi ✅ (Admin role)

**Response:** 204 No Content

## Ishlash tartibi (Frontend uchun)

### Yangi maydon qo'shish

1. **Maydon ma'lumotlarini yaratish**

   ```http
   POST /api/fields/my-fields/create/
   ```

   ```json
   {
     "name": "Yangi Stadion",
     "address": "Sergeli tumani",
     "city": "Toshkent",
     "phone": "+998901234567",
     "price_per_hour": "180000.00",
     "opening_time": "08:00:00",
     "closing_time": "23:00:00"
   }
   ```

2. **Yaratilgan maydon ID sini olish (response dan)**

   ```json
   {
     "id": 3,
     "name": "Yangi Stadion",
     ...
   }
   ```

3. **Maydonga rasmlar yuklash**

   ```http
   POST /api/fields/my-fields/upload-images/
   ```

   Form data:
   - `field_id=3`
   - `images=file1.jpg`
   - `images=file2.jpg`

### Mavjud maydonga rasm qo'shish

1. **O'z maydonlarim ro'yxatini olish**

   ```http
   GET /api/fields/my-fields/
   ```

2. **Kerakli maydon ID sini tanlash**

3. **Rasm yuklash**

   ```http
   POST /api/fields/my-fields/upload-images/
   ```

   Form data:
   - `field_id=1`
   - `images=new_image.jpg`

4. **Yangilangan maydon ma'lumotini olish**

   ```http
   GET /api/fields/my-fields/1/
   ```

   Response da `images` array yangi rasmlar bilan qaytadi.

## Xatolar

### Maydon topilmadi yoki sizga tegishli emas

```json
{
  "detail": "Maydon topilmadi yoki sizga tegishli emas."
}
```

### field_id parametri majburiy

```json
{
  "detail": "field_id parametri majburiy."
}
```

### Hech qanday rasm yuborilmadi

```json
{
  "detail": "Hech qanday rasm yuborilmadi."
}
```

### Rasm topilmadi

```json
{
  "detail": "Rasm topilmadi."
}
```

## Muhim eslatmalar

1. **Bir nechta maydon** - Admin bir nechta maydonga ega bo'lishi mumkin. Har bir maydon alohida boshqariladi.

2. **field_id majburiy** - Rasm yuklashda `field_id` parametri majburiy, chunki admin bir nechta maydonga ega bo'lishi mumkin.

3. **Rasmlar qo'shiladi** - Yangi rasmlar yuklanganda eski rasmlar o'chirilmaydi, balki ro'yxatga qo'shiladi.

4. **images array** - Har bir maydon ma'lumotida `images` array mavjud bo'lib, unda barcha yuklangan rasmlar ro'yxati bor.

5. **Owner avtomatik** - Yangi maydon yaratilganda `owner` avtomatik ravishda joriy admin foydalanuvchiga o'rnatiladi.

6. **Faqat o'z maydonlari** - Admin faqat o'ziga tegishli maydonlarni ko'rishi, tahrirlashi va o'chirishi mumkin.

7. **Superuser** - Superuser barcha maydonlarni ko'rishi va boshqarishi mumkin (admin panel orqali).

## Frontend uchun misol kod (JavaScript)

### Rasm yuklash

```javascript
async function uploadFieldImages(fieldId, imageFiles) {
  const formData = new FormData();
  formData.append('field_id', fieldId);
  
  // Bir nechta rasmlarni qo'shish
  imageFiles.forEach(file => {
    formData.append('images', file);
  });

  const response = await fetch('/api/fields/my-fields/upload-images/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });

  if (response.ok) {
    const uploadedImages = await response.json();
    console.log('Yuklangan rasmlar:', uploadedImages);
    return uploadedImages;
  } else {
    const error = await response.json();
    console.error('Xato:', error);
    throw new Error(error.detail);
  }
}

// Ishlatish
const fileInput = document.getElementById('imageInput');
const fieldId = 1; // Tanlangan maydon ID
await uploadFieldImages(fieldId, fileInput.files);
```

### Yangi maydon yaratish va rasm yuklash

```javascript
async function createFieldWithImages(fieldData, imageFiles) {
  // 1. Maydon yaratish
  const createResponse = await fetch('/api/fields/my-fields/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(fieldData)
  });

  const newField = await createResponse.json();
  console.log('Yangi maydon yaratildi:', newField);

  // 2. Rasmlar yuklash
  if (imageFiles.length > 0) {
    const uploadedImages = await uploadFieldImages(newField.id, imageFiles);
    console.log('Rasmlar yuklandi:', uploadedImages);
  }

  return newField;
}
```
