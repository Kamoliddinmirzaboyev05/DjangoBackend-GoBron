from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('id', 'recipient', 'booking', 'short_message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'recipient')
    search_fields = ('recipient__username', 'message', 'booking__field__name')
    readonly_fields = ('created_at', 'recipient', 'booking', 'message')
    ordering = ('-created_at',)
    list_editable = ('is_read',)

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Xabar'
