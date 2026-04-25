from django.conf import settings
from django.db import models

from apps.fields.models import FootballField, TimeSlot


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    BOOKING_TYPE_CHOICES = [
        ('online', 'Online (foydalanuvchi)'),
        ('manual', 'Qo\'lda (admin)'),
    ]

    field = models.ForeignKey(
        FootballField, on_delete=models.CASCADE,
        related_name='bookings', verbose_name='Maydon'
    )
    slot = models.OneToOneField(
        TimeSlot, on_delete=models.CASCADE,
        related_name='booking', verbose_name='Slot',
        null=True, blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookings', verbose_name='Foydalanuvchi',
        null=True, blank=True,
    )
    # Admin qo'lda band qilganda foydalanuvchi tizimda bo'lmasligi mumkin
    guest_full_name = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='Mijoz ismi (qo\'lda)',
    )
    guest_phone = models.CharField(
        max_length=20, blank=True, null=True,
        verbose_name='Mijoz telefoni (qo\'lda)',
    )
    booking_type = models.CharField(
        max_length=10, choices=BOOKING_TYPE_CHOICES,
        default='online', verbose_name='Bron turi',
    )
    date = models.DateField(verbose_name='Sana')
    start_time = models.TimeField(verbose_name='Boshlanish')
    end_time = models.TimeField(verbose_name='Tugash')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Holat'
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Umumiy narx'
    )
    note = models.TextField(blank=True, null=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='Tasdiqlangan')

    class Meta:
        verbose_name = 'Bron'
        verbose_name_plural = 'Bronlar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', 'date', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        who = self.guest_full_name or (
            self.user.get_full_name() or self.user.username if self.user else '—'
        )
        return (
            f'Bron #{self.pk} — {self.field.name} '
            f'{self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M} '
            f'[{self.get_status_display()}] ({who})'
        )

    @property
    def client_name(self):
        if self.booking_type == 'manual':
            return self.guest_full_name or '—'
        return self.user.get_full_name() or self.user.username if self.user else '—'

    @property
    def client_phone(self):
        if self.booking_type == 'manual':
            return self.guest_phone or '—'
        return self.user.phone if self.user else '—'
