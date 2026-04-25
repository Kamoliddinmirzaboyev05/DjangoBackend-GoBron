from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import FootballField, FieldImage, FieldAmenity, TimeSlot


class FieldImageInline(TabularInline):
    model = FieldImage
    extra = 1
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'
    image_preview.short_description = 'Ko\'rinish'


class FieldAmenityInline(TabularInline):
    model = FieldAmenity
    extra = 1
    fields = ('name', 'icon')


@admin.register(FootballField)
class FootballFieldAdmin(ModelAdmin):
    list_display = (
        'name', 'owner', 'city', 'phone', 'price_per_hour',
        'hours_display', 'advance_booking_days',
        'is_active', 'subscription_badge', 'cover_preview',
    )
    list_filter = ('is_active', 'city', 'is_subscription_active', 'owner')
    search_fields = ('name', 'city', 'address', 'phone', 'owner__username')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'cover_preview', 'subscription_badge')
    inlines = [FieldImageInline, FieldAmenityInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('owner', 'name', 'description', 'address', 'city', 'location_url', 'phone', 'is_active'),
        }),
        ('Narx va vaqt', {
            'fields': ('price_per_hour', 'opening_time', 'closing_time', 'advance_booking_days'),
        }),
        ('Rasm', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('Obuna', {
            'fields': ('subscription_start', 'subscription_end', 'is_subscription_active', 'subscription_badge'),
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def hours_display(self, obj):
        return f'{obj.opening_time:%H:%M} – {obj.closing_time:%H:%M}'
    hours_display.short_description = 'Ish vaqti'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="120" height="80" style="object-fit:cover;border-radius:6px;" />',
                obj.cover_image.url,
            )
        return '—'
    cover_preview.short_description = 'Muqova'

    def subscription_badge(self, obj):
        if obj.subscription_is_valid:
            label = f'Faol → {obj.subscription_end}' if obj.subscription_end else 'Faol (cheksiz)'
            color = '#16a34a'
        else:
            label = f'Tugagan ({obj.subscription_end})' if obj.subscription_end else 'Sozlanmagan'
            color = '#dc2626'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, label,
        )
    subscription_badge.short_description = 'Obuna'


@admin.register(TimeSlot)
class TimeSlotAdmin(ModelAdmin):
    list_display = (
        'field', 'date', 'start_time', 'end_time',
        'is_active', 'active_badge', 'booked_badge',
    )
    list_filter = ('field', 'date', 'is_active', 'is_booked')
    search_fields = ('field__name',)
    list_editable = ('is_active',)
    ordering = ('field', 'date', 'start_time')
    date_hierarchy = 'date'
    readonly_fields = ('is_booked',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(field__owner=request.user)

    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#16a34a;color:#fff;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">Faol</span>'
            )
        return format_html(
            '<span style="background:#6b7280;color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">Nofaol</span>'
        )
    active_badge.short_description = 'Holat'

    def booked_badge(self, obj):
        if obj.is_booked:
            return format_html(
                '<span style="background:#dc2626;color:#fff;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">Band</span>'
            )
        return format_html(
            '<span style="background:#0284c7;color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">Bo\'sh</span>'
        )
    booked_badge.short_description = 'Band'


@admin.register(FieldImage)
class FieldImageAdmin(ModelAdmin):
    list_display = ('field', 'order', 'image_preview', 'created_at')
    list_filter = ('field',)
    search_fields = ('field__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(field__owner=request.user)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'
    image_preview.short_description = 'Ko\'rinish'


@admin.register(FieldAmenity)
class FieldAmenityAdmin(ModelAdmin):
    list_display = ('name', 'icon', 'field')
    list_filter = ('field',)
    search_fields = ('name', 'field__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(field__owner=request.user)
