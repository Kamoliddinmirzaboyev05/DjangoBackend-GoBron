from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        'username', 'full_name', 'phone', 'role_badge',
        'is_active', 'date_joined', 'avatar_preview',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview')

    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('phone', 'role', 'avatar', 'avatar_preview'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'phone', 'role'),
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name() or '—'
    full_name.short_description = 'Ism Familiya'

    def role_badge(self, obj):
        color = '#16a34a' if obj.role == 'admin' else '#2563eb'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_role_display(),
        )
    role_badge.short_description = 'Rol'

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="48" height="48" '
                'style="border-radius:50%;object-fit:cover;" />',
                obj.avatar.url,
            )
        return '—'
    avatar_preview.short_description = 'Avatar'
