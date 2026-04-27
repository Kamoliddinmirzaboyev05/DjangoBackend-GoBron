# Football Field Booking System

A complete Django REST API backend for booking synthetic football fields.

## Tech Stack

- Python 3.11+
- Django 4.2
- Django REST Framework
- Django Jazzmin (admin UI)
- SQLite (dev) / PostgreSQL (prod)
- JWT Authentication (SimpleJWT)
- django-filter, django-cors-headers, Pillow

---

## Project Structure

```
football_booking/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/       # User auth & profiles
│   ├── fields/         # Football fields, images, amenities
│   ├── bookings/       # Booking management
│   ├── notifications/  # Admin notifications
│   └── settings_app/   # Admin API (stats, field mgmt)
├── fixtures/
│   └── initial_data.json
├── static/
├── media/
└── templates/
```

---

## Setup Instructions

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd football_booking
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create default admin

```bash
python manage.py create_superuser_admin
# Default: username=admin, password=Admin@12345
# Options: --username --email --password --phone
```

### 6. Load sample data

```bash
python manage.py loaddata fixtures/initial_data.json
```

### 7. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 8. Run development server

```bash
python manage.py runserver
```

Admin panel: http://127.0.0.1:8000/admin/

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| GET/PUT | `/api/auth/profile/` | Get or update profile |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Fields (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/fields/` | List active fields |
| GET | `/api/fields/?city=Toshkent&price_min=100000&price_max=200000` | Filter fields |
| GET | `/api/fields/{id}/` | Field detail with images & amenities |
| GET | `/api/fields/{id}/available-dates/` | Available booking dates for field |
| GET | `/api/fields/{id}/slots/?date=2025-06-15` | Available time slots (date required) |
| GET | `/api/fields/slots/{slot_id}/` | Get specific slot details |

### Bookings (Authenticated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings/` | Create booking (slot_id required, field_id & date optional for validation) |
| GET | `/api/bookings/my/` | My bookings |
| DELETE | `/api/bookings/{id}/cancel/` | Cancel pending booking |

### Admin API (Admin role only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/bookings/` | All bookings (filter: status, date, field) |
| PATCH | `/api/admin/bookings/{id}/confirm/` | Confirm booking |
| PATCH | `/api/admin/bookings/{id}/reject/` | Reject booking |
| GET | `/api/admin/stats/` | Dashboard statistics |
| GET | `/api/admin/notifications/` | Unread notifications |
| PATCH | `/api/admin/notifications/{id}/read/` | Mark notification read |
| PATCH | `/api/admin/notifications/read-all/` | Mark all read |
| GET/PUT | `/api/admin/fields/{id}/` | View/update field |
| POST | `/api/admin/fields/{id}/images/` | Upload field image |
| DELETE | `/api/admin/fields/{id}/images/{img_id}/` | Delete field image |
| GET/POST | `/api/admin/fields/{id}/amenities/` | List/add amenities |
| DELETE | `/api/admin/fields/{id}/amenities/{amenity_id}/` | Delete amenity |

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Token lifetimes:
- Access token: 60 minutes
- Refresh token: 7 days

---

## Example Requests

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","first_name":"John","phone":"+998901234567","password":"Pass@1234","password2":"Pass@1234"}'
```

### Get Available Dates
```bash
curl http://localhost:8000/api/fields/1/available-dates/
```

### Get Slots for Specific Date
```bash
curl http://localhost:8000/api/fields/1/slots/?date=2025-06-20
```

### Get Specific Slot Details
```bash
curl http://localhost:8000/api/fields/slots/123/
```

### Create Booking (Minimal - only slot_id)
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id":123,"note":"Optional note"}'
```

### Create Booking (With validation - slot_id, field_id, date)
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id":123,"field_id":1,"date":"2025-06-20","note":"Optional note"}'
```

---

## PostgreSQL Setup (Production)

Update `.env`:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=football_booking
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

---

## Pagination

Fields list is paginated at 12 items per page.
```
GET /api/fields/?page=2
```

---

## Management Commands

```bash
# Create default admin user
python manage.py create_superuser_admin

# With custom credentials
python manage.py create_superuser_admin --username myadmin --email admin@mysite.com --password MyPass@123
```
