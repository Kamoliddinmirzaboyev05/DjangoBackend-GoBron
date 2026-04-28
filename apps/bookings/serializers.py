from decimal import Decimal
from datetime import datetime, date as date_type

from rest_framework import serializers

from apps.fields.models import TimeSlot
from apps.fields.serializers import FootballFieldListSerializer
from apps.accounts.serializers import UserSerializer
from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    """Foydalanuvchi tomonidan online bron."""
    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(),
        source='slot',
        write_only=True,
        label='Slot ID',
    )
    field_id = serializers.IntegerField(write_only=True, required=False, help_text='Maydon ID (tekshirish uchun)')
    date = serializers.DateField(write_only=True, required=False, help_text='Sana (tekshirish uchun)')

    class Meta:
        model = Booking
        fields = ('id', 'slot_id', 'field_id', 'date', 'note')

    def validate_slot_id(self, slot):
        if not slot.is_active:
            raise serializers.ValidationError('Bu slot admin tomonidan o\'chirilgan.')
        if slot.is_booked:
            raise serializers.ValidationError('Bu slot allaqachon band.')
        if slot.date < date_type.today():
            raise serializers.ValidationError('O\'tgan vaqtga bron qilib bo\'lmaydi.')
        return slot

    def validate(self, attrs):
        slot = attrs['slot']
        field = slot.field
        
        # Agar field_id berilgan bo'lsa, tekshiramiz
        if 'field_id' in attrs and attrs['field_id'] != field.id:
            raise serializers.ValidationError({
                'field_id': f'Bu slot maydon #{field.id} ga tegishli, lekin siz #{attrs["field_id"]} ni ko\'rsatdingiz.'
            })
        
        # Agar date berilgan bo'lsa, tekshiramiz
        if 'date' in attrs and attrs['date'] != slot.date:
            raise serializers.ValidationError({
                'date': f'Bu slot {slot.date} sanasiga tegishli, lekin siz {attrs["date"]} ni ko\'rsatdingiz.'
            })
        
        from apps.fields.utils import get_available_dates
        if slot.date not in get_available_dates(field):
            raise serializers.ValidationError(
                f'Bu maydon faqat {field.advance_booking_days} kun oldindan bron qilishga ruxsat beradi.'
            )
        if not field.subscription_is_valid:
            raise serializers.ValidationError('Bu maydonning obunasi tugagan.')
        return attrs

    def create(self, validated_data):
        # field_id va date ni olib tashlaymiz, ular faqat validatsiya uchun
        validated_data.pop('field_id', None)
        validated_data.pop('date', None)
        
        slot = validated_data['slot']
        field = slot.field
        start_dt = datetime.combine(slot.date, slot.start_time)
        end_dt = datetime.combine(slot.date, slot.end_time)
        hours = Decimal(str((end_dt - start_dt).seconds / 3600))
        return Booking.objects.create(
            field=field,
            slot=slot,
            user=self.context['request'].user,
            date=slot.date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            total_price=field.price_per_hour * hours,
            status='pending',
            booking_type='online',
            note=validated_data.get('note', ''),
        )


class AdminBookingManualCreateSerializer(serializers.Serializer):
    """Admin tomonidan qo'lda bron — field_id, slot_id, date, full_name, phone, plan."""
    field_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        help_text='Maydon ID (tekshirish uchun)'
    )
    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(),
        label='Slot ID',
    )
    date = serializers.DateField(
        write_only=True, 
        required=False, 
        help_text='Sana (tekshirish uchun)'
    )
    guest_full_name = serializers.CharField(
        max_length=200, 
        label='Mijoz ismi'
    )
    guest_phone = serializers.CharField(
        max_length=20, 
        label='Mijoz telefoni'
    )
    plan = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text='To\'lov summasi (ixtiyoriy, tekin o\'yinlar uchun 0 yoki bo\'sh qoldirish mumkin)'
    )
    note = serializers.CharField(
        required=False, 
        allow_blank=True, 
        label='Izoh'
    )

    def validate_slot_id(self, slot):
        if not slot.is_active:
            raise serializers.ValidationError('Bu slot nofaol.')
        if slot.is_booked:
            raise serializers.ValidationError('Bu slot allaqachon band.')
        return slot

    def validate(self, attrs):
        slot = attrs['slot_id']
        field = slot.field
        
        # Agar field_id berilgan bo'lsa, tekshiramiz
        if 'field_id' in attrs and attrs['field_id'] != field.id:
            raise serializers.ValidationError({
                'field_id': f'Bu slot maydon #{field.id} ga tegishli, lekin siz #{attrs["field_id"]} ni ko\'rsatdingiz.'
            })
        
        # Agar date berilgan bo'lsa, tekshiramiz
        if 'date' in attrs and attrs['date'] != slot.date:
            raise serializers.ValidationError({
                'date': f'Bu slot {slot.date} sanasiga tegishli, lekin siz {attrs["date"]} ni ko\'rsatdingiz.'
            })
        
        return attrs

    def create(self, validated_data):
        # field_id va date ni olib tashlaymiz, ular faqat validatsiya uchun
        validated_data.pop('field_id', None)
        validated_data.pop('date', None)
        
        slot = validated_data['slot_id']
        field = slot.field
        start_dt = datetime.combine(slot.date, slot.start_time)
        end_dt = datetime.combine(slot.date, slot.end_time)
        hours = Decimal(str((end_dt - start_dt).seconds / 3600))
        
        # Agar plan berilgan bo'lsa, uni ishlatamiz, aks holda avtomatik hisoblash
        if 'plan' in validated_data and validated_data['plan'] is not None:
            total_price = validated_data['plan']
        else:
            total_price = field.price_per_hour * hours

        booking = Booking.objects.create(
            field=field,
            slot=slot,
            user=None,
            guest_full_name=validated_data['guest_full_name'],
            guest_phone=validated_data['guest_phone'],
            date=slot.date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            total_price=total_price,
            status='confirmed',   # admin qo'lda qo'shsa — darhol tasdiqlangan
            booking_type='manual',
            note=validated_data.get('note', ''),
            confirmed_at=__import__('django.utils.timezone', fromlist=['timezone']).timezone.now(),
        )
        # Slotni band qilish
        slot.is_booked = True
        slot.save(update_fields=['is_booked'])
        return booking


class BookingSerializer(serializers.ModelSerializer):
    field_detail = FootballFieldListSerializer(source='field', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    booking_type_display = serializers.CharField(source='get_booking_type_display', read_only=True)
    client_name = serializers.CharField(read_only=True)
    client_phone = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'field', 'field_detail', 'slot', 'user', 'user_detail',
            'guest_full_name', 'guest_phone',
            'booking_type', 'booking_type_display',
            'client_name', 'client_phone',
            'date', 'start_time', 'end_time', 'status', 'status_display',
            'total_price', 'note', 'created_at', 'confirmed_at',
        )
        read_only_fields = (
            'id', 'field', 'slot', 'user', 'status',
            'total_price', 'created_at', 'confirmed_at',
        )


class BookingAdminSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    field_city = serializers.CharField(source='field.city', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    booking_type_display = serializers.CharField(source='get_booking_type_display', read_only=True)
    client_name = serializers.CharField(read_only=True)
    client_phone = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'field', 'field_name', 'field_city',
            'user', 'guest_full_name', 'guest_phone',
            'booking_type', 'booking_type_display',
            'client_name', 'client_phone',
            'date', 'start_time', 'end_time',
            'status', 'status_display', 'total_price',
            'note', 'created_at', 'confirmed_at',
        )
        read_only_fields = fields
