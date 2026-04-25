from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Notification


class BookingInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    field_name = serializers.CharField()
    date = serializers.CharField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    status = serializers.CharField()
    user = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    booking_info = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'booking', 'booking_info',
            'message', 'is_read', 'created_at',
        )
        read_only_fields = fields

    @extend_schema_field(BookingInfoSerializer)
    def get_booking_info(self, obj):
        booking = obj.booking
        return {
            'id': booking.pk,
            'field_name': booking.field.name,
            'date': str(booking.date),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'status': booking.status,
            'user': booking.client_name,
        }
