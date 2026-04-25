from decimal import Decimal
from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action

from apps.fields.models import TimeSlot
from .models import Booking


# ─── Custom form for manual booking ──────────────────────────────────────────

class ManualBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            'field', 'slot', 'guest_full_name', 'guest_phone',
            'note', 'status', 'total_price',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat bo'sh slotlarni ko'rsatish
        self.fields['slot'].queryset = TimeSlot.objects.filter(
            is_booked=False, is_active=True
        ).select_related('field').order_by('field', 'date', 'start_time')
        self.fields['slot'].label_from_instance = lambda s: (
            f'{s.field.name} | {s.date} {s.start_time:%H:%M}-{s.end_time:%H:%M}'
        )
        self.fields['total_price'].required = False
        self.fields['status'].initial = 'confirmed'


# ─── Actions ──────────────────────────────────────────────────────────────────

def confirm_bookings(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.filter(status='pending'):
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save(update_fields=['status', 'confirmed_at'])
        if booking.slot:
            booking.slot.is_booked = True
            booking.slot.save(update_fields=['is_booked'])
        updated += 1
    modeladmin.message_user(request, f'{updated} ta bron tasdiqlandi.', messages.SUCCESS)
confirm_bookings.short_description = '✅ Tanlangan bronlarni tasdiqlash'


def reject_bookings(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.filter(status__in=['pending', 'confirmed']):
        if booking.slot and booking.status == 'confirmed':
            booking.slot.is_booked = False
            booking.slot.save(update_fields=['is_booked'])
        booking.status = 'rejected'
        booking.save(update_fields=['status'])
        updated += 1
    modeladmin.message_user(request, f'{updated} ta bron rad etildi.', messages.WARNING)
reject_bookings.short_description = '❌ Tanlangan bronlarni rad etish'


# ─── BookingAdmin ─────────────────────────────────────────────────────────────

@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    form = ManualBookingForm
    list_display = (
        'id', 'field', 'client_display', 'client_phone_display',
        'date', 'time_range', 'type_badge', 'status_badge', 'total_price', 'created_at',
    )
    list_filter = ('status', 'booking_type', 'date', 'field')
    search_fields = (
        'field__name', 'user__username', 'user__first_name',
        'user__last_name', 'user__phone',
        'guest_full_name', 'guest_phone',
    )
    readonly_fields = ('created_at', 'confirmed_at', 'total_price', 'booking_type')
    ordering = ('-created_at',)
    actions = [confirm_bookings, reject_bookings]
    date_hierarchy = 'date'

    fieldsets = (
        ('Bron ma\'lumotlari', {
            'fields': ('field', 'slot', 'booking_type'),
        }),
        ('Mijoz', {
            'fields': ('user', 'guest_full_name', 'guest_phone'),
            'description': 'Online bron uchun "user", qo\'lda bron uchun "guest" maydonlarini to\'ldiring.',
        }),
        ('Vaqt va narx', {
            'fields': ('date', 'start_time', 'end_time', 'total_price'),
        }),
        ('Holat', {
            'fields': ('status', 'note'),
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'confirmed_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            # Yangi qo'lda bron
            obj.booking_type = 'manual'
            if obj.slot:
                field = obj.slot.field
                obj.field = field
                obj.date = obj.slot.date
                obj.start_time = obj.slot.start_time
                obj.end_time = obj.slot.end_time
                # Narx hisoblash
                if not obj.total_price:
                    start_dt = datetime.combine(obj.slot.date, obj.slot.start_time)
                    end_dt = datetime.combine(obj.slot.date, obj.slot.end_time)
                    hours = Decimal(str((end_dt - start_dt).seconds / 3600))
                    obj.total_price = field.price_per_hour * hours
                if obj.status == 'confirmed':
                    obj.confirmed_at = timezone.now()
            obj.save()
            # Slotni band qilish
            if obj.slot and obj.status == 'confirmed':
                obj.slot.is_booked = True
                obj.slot.save(update_fields=['is_booked'])
        else:
            obj.save()

    def client_display(self, obj):
        return obj.client_name
    client_display.short_description = 'Mijoz'

    def client_phone_display(self, obj):
        return obj.client_phone
    client_phone_display.short_description = 'Telefon'

    def time_range(self, obj):
        return f'{obj.start_time:%H:%M} – {obj.end_time:%H:%M}'
    time_range.short_description = 'Vaqt'

    def type_badge(self, obj):
        if obj.booking_type == 'manual':
            return format_html(
                '<span style="background:#7c3aed;color:#fff;padding:2px 8px;'
                'border-radius:12px;font-size:11px;font-weight:600;">Qo\'lda</span>'
            )
        return format_html(
            '<span style="background:#0284c7;color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600;">Online</span>'
        )
    type_badge.short_description = 'Tur'

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#16a34a',
            'rejected': '#dc2626',
            'cancelled': '#6b7280',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#333'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Holat'
