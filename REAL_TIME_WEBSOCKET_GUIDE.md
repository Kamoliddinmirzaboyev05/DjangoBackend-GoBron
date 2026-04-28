# Real-time Updates uchun qo'llanma

## Umumiy ma'lumot

Real-time yangilanishlar uchun Django Channels va WebSocket ishlatiladi. Bu sahifani yangilamasdan yangilanishlarni olish imkonini beradi.

## Kerakli paketlar

```bash
pip install channels channels-redis daphne
```

## O'rnatish qadamlari

### 1. settings.py ga qo'shish

```python
INSTALLED_APPS = [
    'daphne',  # Eng yuqorida
    # ... boshqa ilovalar
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # Development uchun
        # Production uchun Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    },
}
```

### 2. asgi.py yaratish

`config/asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from apps.bookings import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
```

### 3. Consumer yaratish

`apps/bookings/consumers.py`:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bookings'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def booking_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'booking_update',
            'data': event['data']
        }))
```

### 4. Routing yaratish

`apps/bookings/routing.py`:

```python
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/bookings/', consumers.BookingConsumer.as_asgi()),
]
```

### 5. Signal qo'shish

`apps/bookings/signals.py` ga qo'shish:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Booking
from .serializers import BookingAdminSerializer

@receiver(post_save, sender=Booking)
def booking_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    serializer = BookingAdminSerializer(instance)
    
    async_to_sync(channel_layer.group_send)(
        'bookings',
        {
            'type': 'booking_update',
            'data': {
                'action': 'created' if created else 'updated',
                'booking': serializer.data
            }
        }
    )

@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'bookings',
        {
            'type': 'booking_update',
            'data': {
                'action': 'deleted',
                'booking_id': instance.id
            }
        }
    )
```

## Frontend (JavaScript)

```javascript
// WebSocket ulanish
const ws = new WebSocket('ws://localhost:8000/ws/bookings/');

ws.onopen = () => {
    console.log('WebSocket ulandi');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'booking_update') {
        const { action, booking, booking_id } = data.data;
        
        switch (action) {
            case 'created':
                console.log('Yangi bron:', booking);
                // UI ga qo'shish
                addBookingToUI(booking);
                break;
            
            case 'updated':
                console.log('Bron yangilandi:', booking);
                // UI da yangilash
                updateBookingInUI(booking);
                break;
            
            case 'deleted':
                console.log('Bron o\'chirildi:', booking_id);
                // UI dan o\'chirish
                removeBookingFromUI(booking_id);
                break;
        }
    }
};

ws.onclose = () => {
    console.log('WebSocket uzildi');
    // Qayta ulanish
    setTimeout(() => {
        location.reload();
    }, 3000);
};

ws.onerror = (error) => {
    console.error('WebSocket xato:', error);
};
```

## Ishga tushirish

### Development

```bash
# Daphne bilan
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Yoki manage.py bilan
python manage.py runserver
```

### Production

```bash
# Daphne
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Yoki Gunicorn + Uvicorn
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
```

## Redis o'rnatish (Production uchun)

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis
```

## Test qilish

```python
# Django shell
python manage.py shell

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    'bookings',
    {
        'type': 'booking_update',
        'data': {'test': 'Hello WebSocket!'}
    }
)
```

## Muhim eslatmalar

1. **Development**: InMemoryChannelLayer ishlatiladi (bir server uchun)
2. **Production**: Redis ishlatiladi (bir nechta server uchun)
3. **CORS**: WebSocket uchun CORS sozlamalari kerak
4. **Auth**: WebSocket uchun JWT token yuborish kerak
5. **Reconnect**: Ulanish uzilsa avtomatik qayta ulanish kerak

## Muqobil yechim: Server-Sent Events (SSE)

Agar WebSocket murakkab bo'lsa, SSE ishlatish mumkin:

```python
# views.py
from django.http import StreamingHttpResponse
import json
import time

def booking_stream(request):
    def event_stream():
        while True:
            # Yangilanishlarni tekshirish
            yield f"data: {json.dumps({'message': 'ping'})}\n\n"
            time.sleep(5)
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
```

```javascript
// Frontend
const eventSource = new EventSource('/api/bookings/stream/');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Yangilanish:', data);
};
```

SSE oddiyroq lekin bir tomonlama (server → client).
