import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

DJANGO_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.fields',
    'apps.bookings',
    'apps.notifications',
    'apps.settings_app',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')
if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': config('DB_NAME', default='football_booking'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True 

# Cookie va Tokenlarni yuborishga ruxsat berish
CORS_ALLOW_CREDENTIALS = True

# drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Football Booking API',
    'DESCRIPTION': (
        '## Futbol maydonlarini bron qilish tizimi\n\n'
        '### Autentifikatsiya qilish:\n\n'
        '1. `/api/auth/login/` endpointiga username va password yuboring\n'
        '2. Response dan `access` tokenni nusxalang\n'
        '3. Yuqoridagi **"Authorize"** tugmasini bosing\n'
        '4. Tokenni kiriting (faqat token, "Bearer" so\'zisiz)\n'
        '5. "Authorize" tugmasini bosing\n\n'
        '**Eslatma:** Token avtomatik ravishda barcha so\'rovlarga qo\'shiladi.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
        'defaultModelsExpandDepth': 1,
        'defaultModelExpandDepth': 1,
        'docExpansion': 'list',
    },
    'TAGS': [
        {'name': 'Auth', 'description': 'Ro\'yxatdan o\'tish, kirish, chiqish, profil'},
        {'name': 'Fields', 'description': 'Futbol maydonlari ro\'yxati va tafsilotlari'},
        {'name': 'Fields Admin', 'description': 'Admin: o\'z maydonlarini boshqarish'},
        {'name': 'Slots', 'description': 'Vaqt slotlari — ko\'rish va boshqarish'},
        {'name': 'Bookings', 'description': 'Bron qilish — yaratish va bekor qilish'},
        {'name': 'Admin — Fields', 'description': 'Admin: maydonlarni boshqarish'},
        {'name': 'Admin — Bookings', 'description': 'Admin: bronlarni tasdiqlash/rad etish'},
        {'name': 'Admin — Stats', 'description': 'Admin: statistika'},
        {'name': 'Admin — Notifications', 'description': 'Admin: bildirishnomalar'},
    ],
}

# Unfold Admin
UNFOLD = {
    'SITE_TITLE': 'Football Booking',
    'SITE_HEADER': 'Futbol Maydonlari Admin',
    'SITE_SUBHEADER': 'Boshqaruv paneli',
    'SITE_URL': '/',
    'SITE_ICON': None,
    'SITE_SYMBOL': 'sports_soccer',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': False,
    'ENVIRONMENT': 'config.settings.environment_callback',
    'DASHBOARD_CALLBACK': None,
    'COLORS': {
        'primary': {
            '50': '240 253 244',
            '100': '220 252 231',
            '200': '187 247 208',
            '300': '134 239 172',
            '400': '74 222 128',
            '500': '34 197 94',
            '600': '22 163 74',
            '700': '21 128 61',
            '800': '22 101 52',
            '900': '20 83 45',
            '950': '5 46 22',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Asosiy',
                'separator': False,
                'items': [
                    {
                        'title': 'Boshqaruv paneli',
                        'icon': 'dashboard',
                        'link': '/admin/',
                    },
                ],
            },
            {
                'title': 'Foydalanuvchilar',
                'separator': True,
                'items': [
                    {
                        'title': 'Foydalanuvchilar',
                        'icon': 'people',
                        'link': '/admin/accounts/customuser/',
                    },
                ],
            },
            {
                'title': 'Maydonlar',
                'separator': True,
                'items': [
                    {
                        'title': 'Futbol maydonlari',
                        'icon': 'sports_soccer',
                        'link': '/admin/fields/footballfield/',
                    },
                    {
                        'title': 'Slotlar',
                        'icon': 'schedule',
                        'link': '/admin/fields/timeslot/',
                    },
                    {
                        'title': 'Rasmlar',
                        'icon': 'image',
                        'link': '/admin/fields/fieldimage/',
                    },
                    {
                        'title': 'Qulayliklar',
                        'icon': 'star',
                        'link': '/admin/fields/fieldamenity/',
                    },
                ],
            },
            {
                'title': 'Bronlar',
                'separator': True,
                'items': [
                    {
                        'title': 'Bronlar',
                        'icon': 'calendar_month',
                        'link': '/admin/bookings/booking/',
                    },
                ],
            },
            {
                'title': 'Bildirishnomalar',
                'separator': True,
                'items': [
                    {
                        'title': 'Bildirishnomalar',
                        'icon': 'notifications',
                        'link': '/admin/booking_notifications/notification/',
                    },
                ],
            },
        ],
    },
}


def environment_callback(request):
    return ['Development', 'warning'] if DEBUG else ['Production', 'danger']
