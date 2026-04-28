from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import CustomUser, MagicToken, Stadium, UserSession, OTPCode


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        'phone_number', 'full_name', 'user_role_badge', 'telegram_id',
        'is_phone_verified', 'is_active', 'date_joined', 'avatar_preview',
    )
    list_filter = ('user_role', 'is_phone_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'full_name', 'telegram_username', 'telegram_id')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('full_name', 'email', 'avatar', 'avatar_preview')
        }),
        ('Telegram', {
            'fields': ('telegram_id', 'telegram_username')
        }),
        ('Ruxsatlar', {
            'fields': ('user_role', 'is_phone_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'user_role', 'telegram_id', 'password1', 'password2'),
        }),
    )

    def user_role_badge(self, obj):
        color = '#16a34a' if obj.user_role == 'OWNER' else '#2563eb'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_user_role_display(),
        )
    user_role_badge.short_description = 'Rol'

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="48" height="48" '
                'style="border-radius:50%;object-fit:cover;" />',
                obj.avatar.url,
            )
        return '—'
    avatar_preview.short_description = 'Avatar'


@admin.register(MagicToken)
class MagicTokenAdmin(ModelAdmin):
    list_display = ('user', 'token_short', 'created_at', 'expires_at', 'is_used', 'is_valid_display')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__phone_number', 'user__full_name', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_valid_display')

    def token_short(self, obj):
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'

    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html(
                '<span style="color:#16a34a;font-weight:600;">✓ Faol</span>'
            )
        elif obj.is_used:
            return format_html(
                '<span style="color:#dc2626;font-weight:600;">✗ Ishlatilgan</span>'
            )
        else:
            return format_html(
                '<span style="color:#f59e0b;font-weight:600;">⏰ Muddati tugagan</span>'
            )
    is_valid_display.short_description = 'Holat'


@admin.register(Stadium)
class StadiumAdmin(ModelAdmin):
    list_display = ('name', 'owner', 'hourly_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'owner__user_role')
    search_fields = ('name', 'address', 'owner__phone_number', 'owner__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'address', 'hourly_rate')
        }),
        ('Qo\'shimcha', {
            'fields': ('description', 'is_active')
        }),
        ('Vaqt belgilari', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(ModelAdmin):
    list_display = ('user', 'telegram_id', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__phone_number', 'user__full_name', 'telegram_id')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = (
        'phone_number', 'code', 'user_role_badge', 'telegram_id',
        'is_verified', 'attempts', 'status_display', 'created_at', 'expires_at'
    )
    list_filter = ('user_role', 'is_verified', 'created_at', 'expires_at')
    search_fields = ('phone_number', 'full_name', 'telegram_id', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('code', 'created_at', 'expires_at', 'status_display')

    fieldsets = (
        (None, {
            'fields': ('phone_number', 'telegram_id', 'code')
        }),
        ('Foydalanuvchi ma\'lumotlari', {
            'fields': ('user_role', 'full_name', 'telegram_username')
        }),
        ('Tasdiqlash', {
            'fields': ('is_verified', 'attempts', 'status_display')
        }),
        ('Vaqt belgilari', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    def user_role_badge(self, obj):
        color = '#16a34a' if obj.user_role == 'OWNER' else '#2563eb'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_user_role_display(),
        )
    user_role_badge.short_description = 'Rol'

    def status_display(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="color:#16a34a;font-weight:600;">✓ Tasdiqlangan</span>'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="color:#f59e0b;font-weight:600;">⏰ Muddati tugagan</span>'
            )
        elif obj.attempts >= 3:
            return format_html(
                '<span style="color:#dc2626;font-weight:600;">🚫 Bloklangan</span>'
            )
        else:
            return format_html(
                '<span style="color:#2563eb;font-weight:600;">⏳ Kutilmoqda</span>'
            )
    status_display.short_description = 'Holat'
