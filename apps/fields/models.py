from django.conf import settings
from django.db import models
from django.utils import timezone


class FootballField(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='owned_fields',
        verbose_name='Egasi (admin)',
        limit_choices_to={'role': 'admin'},
    )
    name = models.CharField(max_length=200, verbose_name='Nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    address = models.CharField(max_length=300, verbose_name='Manzil')
    city = models.CharField(max_length=100, verbose_name='Shahar')
    location_url = models.URLField(
        blank=True, null=True,
        verbose_name='Joylashuv (Google Maps URL)',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon raqami')
    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Narx (soatiga)'
    )
    opening_time = models.TimeField(help_text='e.g. 08:00', verbose_name='Ochilish vaqti')
    closing_time = models.TimeField(help_text='e.g. 02:00', verbose_name='Yopilish vaqti')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    cover_image = models.ImageField(
        upload_to='fields/covers/', blank=True, null=True, verbose_name='Muqova rasmi'
    )

    # Obuna
    subscription_start = models.DateField(
        null=True, blank=True, verbose_name='Obuna boshlanish sanasi'
    )
    subscription_end = models.DateField(
        null=True, blank=True, verbose_name='Obuna tugash sanasi'
    )
    is_subscription_active = models.BooleanField(
        default=True, verbose_name='Obuna faol'
    )

    # Necha kun oldindan bron qilish mumkin
    advance_booking_days = models.PositiveIntegerField(
        default=1,
        verbose_name='Oldindan bron qilish (kun)',
        help_text='Foydalanuvchi necha kun oldindan bron qila oladi (1, 3, 7...)',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')

    class Meta:
        verbose_name = 'Futbol maydoni'
        verbose_name_plural = 'Futbol maydonlari'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.city}'

    @property
    def subscription_is_valid(self):
        """Obuna hozir amalda ekanligini tekshiradi."""
        if not self.is_subscription_active:
            return False
        today = timezone.now().date()
        if self.subscription_end and today > self.subscription_end:
            return False
        return True


class FieldImage(models.Model):
    field = models.ForeignKey(
        FootballField, on_delete=models.CASCADE,
        related_name='images', verbose_name='Maydon'
    )
    image = models.ImageField(upload_to='fields/images/', verbose_name='Rasm')
    order = models.IntegerField(default=0, verbose_name='Tartib')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Maydon rasmi'
        verbose_name_plural = 'Maydon rasmlari'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Rasm #{self.order} — {self.field.name}'


class FieldAmenity(models.Model):
    field = models.ForeignKey(
        FootballField, on_delete=models.CASCADE,
        related_name='amenities', verbose_name='Maydon'
    )
    name = models.CharField(
        max_length=100,
        help_text='e.g. Kiyinish xonasi, Parking',
        verbose_name='Nomi',
    )
    icon = models.CharField(
        max_length=50, help_text='Icon nomi yoki emoji', blank=True, verbose_name='Icon'
    )

    class Meta:
        verbose_name = 'Qulaylik'
        verbose_name_plural = 'Qulayliklar'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.field.name})'


class TimeSlot(models.Model):
    """
    Har bir maydon uchun har bir kun uchun avtomatik yoki qo'lda yaratilgan slot.
    Slot yaratilganda avtomatik generate qilinadi.
    """
    field = models.ForeignKey(
        FootballField, on_delete=models.CASCADE,
        related_name='slots', verbose_name='Maydon'
    )
    date = models.DateField(verbose_name='Sana')
    start_time = models.TimeField(verbose_name='Boshlanish vaqti')
    end_time = models.TimeField(verbose_name='Tugash vaqti')
    is_active = models.BooleanField(
        default=True,
        verbose_name='Faol',
        help_text='Admin bu slotni o\'chirib qo\'yishi mumkin',
    )
    is_booked = models.BooleanField(default=False, verbose_name='Band')

    class Meta:
        verbose_name = 'Vaqt sloti'
        verbose_name_plural = 'Vaqt slotlari'
        ordering = ['date', 'start_time']
        unique_together = ('field', 'date', 'start_time')
        indexes = [
            models.Index(fields=['field', 'date', 'is_active', 'is_booked']),
        ]

    def __str__(self):
        status = 'Band' if self.is_booked else ('Faol' if self.is_active else 'Nofaol')
        return f'{self.field.name} | {self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M} [{status}]'
