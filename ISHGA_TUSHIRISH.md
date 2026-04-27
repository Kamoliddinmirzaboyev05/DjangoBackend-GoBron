# Loyihani ishga tushirish qo'llanmasi

## 1. Virtual muhitni faollashtirish

### macOS/Linux:
```bash
source venv/bin/activate
```

### Windows:
```bash
venv\Scripts\activate
```

## 2. Migratsiyalarni tekshirish (agar kerak bo'lsa)

```bash
python manage.py migrate
```

## 3. Loyihani ishga tushirish

```bash
python manage.py runserver
```

Yoki boshqa portda ishga tushirish:
```bash
python manage.py runserver 8080
```

## 4. Brauzerda ochish

- **API Root**: <http://127.0.0.1:8000/api/>
- **Admin Panel**: <http://127.0.0.1:8000/admin/>
- **API Dokumentatsiya (Swagger)**: <http://127.0.0.1:8000/api/schema/swagger-ui/>
- **API Dokumentatsiya (ReDoc)**: <http://127.0.0.1:8000/api/schema/redoc/>

## 5. Swagger UI da autentifikatsiya

Swagger UI da API'larni test qilish uchun:

1. **Login qiling**: `/api/auth/login/` endpointiga username va password yuboring
2. **Token nusxalang**: Response dan `access` tokenni nusxalang
3. **Authorize bosing**: Sahifa yuqorisidagi **"Authorize"** 🔓 tugmasini bosing
4. **Token kiriting**: Tokenni kiriting (faqat token, "Bearer" so'zisiz)
5. **Authorize bosing**: Oynada "Authorize" tugmasini bosing

**Batafsil qo'llanma**: `SWAGGER_AUTH_GUIDE.md` faylini o'qing

## 6. Admin kirish ma'lumotlari

Agar default admin yaratilgan bo'lsa:
- **Username**: admin
- **Password**: Admin@12345

## 6. Loyihani to'xtatish

Terminal'da `Ctrl + C` bosing

---

## Qo'shimcha buyruqlar

### Yangi admin yaratish
```bash
python manage.py create_superuser_admin
```

Yoki maxsus ma'lumotlar bilan:
```bash
python manage.py create_superuser_admin --username myadmin --email admin@example.com --password MyPass@123 --phone +998901234567
```

### Test ma'lumotlarini yuklash
```bash
python manage.py loaddata fixtures/initial_data.json
```

### Static fayllarni yig'ish (production uchun)
```bash
python manage.py collectstatic --noinput
```

### Yangi migratsiya yaratish (model o'zgarganda)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Django shell ochish
```bash
python manage.py shell
```

---

## Muammolarni hal qilish

### Agar port band bo'lsa:
```bash
# Boshqa portda ishga tushiring
python manage.py runserver 8080
```

### Agar virtual muhit ishlamasa:
```bash
# Yangi virtual muhit yarating
python -m venv venv

# Faollashtiring va paketlarni o'rnating
source venv/bin/activate  # yoki Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Agar database xatosi bo'lsa:
```bash
# Database'ni qayta yarating
rm db.sqlite3
python manage.py migrate
python manage.py create_superuser_admin
python manage.py loaddata fixtures/initial_data.json
```

---

## Tezkor ishga tushirish (bitta buyruq)

### macOS/Linux:
```bash
source venv/bin/activate && python manage.py runserver
```

### Windows:
```bash
venv\Scripts\activate && python manage.py runserver
```

---

## Production uchun

Production muhitda ishga tushirish uchun:

1. **Gunicorn bilan** (Linux/macOS):
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

2. **uWSGI bilan**:
```bash
pip install uwsgi
uwsgi --http :8000 --module config.wsgi
```

3. **Nginx + Gunicorn** (tavsiya etiladi):
```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

---

## Environment o'zgaruvchilari

`.env` faylida quyidagi parametrlarni sozlang:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL uchun)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=football_booking
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# SQLite uchun (default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

---

## Foydali havolalar

- Django dokumentatsiya: <https://docs.djangoproject.com/>
- DRF dokumentatsiya: <https://www.django-rest-framework.org/>
- Swagger autentifikatsiya: `SWAGGER_AUTH_GUIDE.md`
- Admin maydonlar qo'llanmasi: `API_ADMIN_FIELDS_GUIDE.md`
- Slotlar API qo'llanmasi: `API_SLOTS_GUIDE.md`
- Loyiha README: `README.md`
