from datetime import date, timedelta

from django.db.models import Sum, Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from apps.accounts.models import CustomUser
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingAdminSerializer, AdminBookingManualCreateSerializer
from apps.fields.models import FootballField, FieldImage, FieldAmenity, TimeSlot
from apps.fields.serializers import (
    FootballFieldDetailSerializer,
    FootballFieldWriteSerializer,
    FieldImageUploadSerializer,
    FieldAmenityWriteSerializer,
    FieldAmenitySerializer,
    TimeSlotSerializer,
    TimeSlotAdminSerializer,
)
from apps.notifications.models import Notification


# ─── Booking Management ──────────────────────────────────────────────────────

@extend_schema(tags=['Admin — Bookings'])
class AdminBookingListView(generics.ListAPIView):
    """Barcha bronlar ro'yxati (filter: status, date, field)."""
    permission_classes = [IsAdminRole]
    serializer_class = BookingAdminSerializer

    def get_queryset(self):
        qs = Booking.objects.select_related('field', 'user').order_by('-created_at')
        p = self.request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('date'):
            qs = qs.filter(date=p['date'])
        if p.get('field'):
            qs = qs.filter(field_id=p['field'])
        return qs


@extend_schema(tags=['Admin — Bookings'])
class AdminBookingConfirmView(APIView):
    """Bronni tasdiqlash."""
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'detail': 'Bron topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != 'pending':
            return Response(
                {'detail': f'Faqat kutilayotgan bronni tasdiqlash mumkin. Holat: "{booking.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save(update_fields=['status', 'confirmed_at'])

        # Slotni band qilish
        if booking.slot:
            booking.slot.is_booked = True
            booking.slot.save(update_fields=['is_booked'])

        Notification.objects.create(
            recipient=booking.user,
            booking=booking,
            message=(
                f'Sizning #{booking.pk} broningiz tasdiqlandi: '
                f'{booking.field.name}, {booking.date} '
                f'{booking.start_time:%H:%M}-{booking.end_time:%H:%M}.'
            ),
        )
        return Response(BookingAdminSerializer(booking).data)


@extend_schema(tags=['Admin — Bookings'])
class AdminBookingRejectView(APIView):
    """Bronni rad etish."""
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'detail': 'Bron topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if booking.status not in ('pending', 'confirmed'):
            return Response(
                {'detail': f'Bu bronni rad etib bo\'lmaydi. Holat: "{booking.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Agar tasdiqlangan bo'lsa slotni bo'shatish
        if booking.slot and booking.status == 'confirmed':
            booking.slot.is_booked = False
            booking.slot.save(update_fields=['is_booked'])

        booking.status = 'rejected'
        booking.save(update_fields=['status'])

        Notification.objects.create(
            recipient=booking.user,
            booking=booking,
            message=(
                f'Sizning #{booking.pk} broningiz rad etildi: '
                f'{booking.field.name}, {booking.date} '
                f'{booking.start_time:%H:%M}-{booking.end_time:%H:%M}.'
            ),
        )
        return Response(BookingAdminSerializer(booking).data)


@extend_schema(tags=['Admin — Bookings'])
class AdminBookingManualCreateView(APIView):
    """Admin tomonidan qo'lda slot band qilish (slot_id, full_name, phone)."""
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = AdminBookingManualCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingAdminSerializer(booking).data, status=status.HTTP_201_CREATED)


# ─── Statistics ───────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin — Stats'])
class AdminStatsView(APIView):
    """Umumiy statistika: bronlar, daromad, maydonlar."""
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        last_30 = today - timedelta(days=29)

        confirmed = Booking.objects.filter(status='confirmed')

        def revenue(qs):
            total = qs.aggregate(t=Sum('total_price'))['t']
            return float(total) if total else 0.0

        # Kunlik bronlar (so'nggi 30 kun) - sodda usul
        per_day_data = []
        for i in range(30):
            day = last_30 + timedelta(days=i)
            day_bookings = Booking.objects.filter(date=day)
            day_revenue = day_bookings.filter(status='confirmed').aggregate(t=Sum('total_price'))['t']
            per_day_data.append({
                'date': str(day),
                'bookings': day_bookings.count(),
                'revenue': float(day_revenue) if day_revenue else 0.0,
            })

        # Status bo'yicha
        status_counts = {
            s: Booking.objects.filter(status=s).count()
            for s, _ in Booking.STATUS_CHOICES
        }

        # Top maydonlar (bronlar soni bo'yicha)
        top_fields_data = []
        fields_with_bookings = (
            Booking.objects.filter(status='confirmed')
            .values_list('field_id', flat=True)
            .distinct()
        )
        
        for field_id in fields_with_bookings[:5]:
            field_bookings = Booking.objects.filter(field_id=field_id, status='confirmed')
            field = FootballField.objects.get(id=field_id)
            field_revenue = field_bookings.aggregate(t=Sum('total_price'))['t']
            top_fields_data.append({
                'field_id': field.id,
                'field_name': field.name,
                'bookings': field_bookings.count(),
                'revenue': float(field_revenue) if field_revenue else 0.0,
            })
        
        # Bronlar soni bo'yicha saralash
        top_fields_data.sort(key=lambda x: x['bookings'], reverse=True)

        return Response({
            'today': {
                'bookings': Booking.objects.filter(date=today).count(),
                'revenue': revenue(confirmed.filter(date=today)),
            },
            'week': {
                'bookings': Booking.objects.filter(date__gte=week_start).count(),
                'revenue': revenue(confirmed.filter(date__gte=week_start)),
            },
            'month': {
                'bookings': Booking.objects.filter(date__gte=month_start).count(),
                'revenue': revenue(confirmed.filter(date__gte=month_start)),
            },
            'total': {
                'bookings': Booking.objects.count(),
                'revenue': revenue(confirmed),
                'fields': FootballField.objects.filter(is_active=True).count(),
                'users': CustomUser.objects.filter(role='user').count(),
            },
            'by_status': status_counts,
            'per_day_last_30': per_day_data,
            'top_fields': top_fields_data[:5],
            'unread_notifications': Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count(),
        })


# ─── Field Management ─────────────────────────────────────────────────────────

@extend_schema(tags=['Admin — Fields'])
class AdminFieldListCreateView(generics.ListCreateAPIView):
    """Admin o'z maydonlari ro'yxati va yangi maydon qo'shish."""
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FootballFieldWriteSerializer
        return FootballFieldDetailSerializer

    def get_queryset(self):
        # Superuser barcha maydonlarni ko'radi, oddiy admin faqat o'zinikini
        user = self.request.user
        if user.is_superuser:
            return FootballField.objects.prefetch_related('images', 'amenities').order_by('-created_at')
        return FootballField.objects.filter(owner=user).prefetch_related('images', 'amenities').order_by('-created_at')

    def perform_create(self, serializer):
        # owner ko'rsatilmasa — avtomatik request.user
        if not serializer.validated_data.get('owner'):
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


@extend_schema(tags=['Admin — Fields'])
class AdminFieldDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Maydon ko'rish, tahrirlash, o'chirish."""
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return FootballField.objects.prefetch_related('images', 'amenities')
        return FootballField.objects.filter(owner=user).prefetch_related('images', 'amenities')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return FootballFieldWriteSerializer
        return FootballFieldDetailSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Admin — Fields'])
class AdminFieldImageUploadView(APIView):
    """Maydon uchun rasm yuklash."""
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FieldImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(field=field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin — Fields'])
class AdminFieldImageDeleteView(APIView):
    """Maydon rasmini o'chirish."""
    permission_classes = [IsAdminRole]

    def delete(self, request, pk, img_id):
        try:
            image = FieldImage.objects.get(pk=img_id, field_id=pk)
        except FieldImage.DoesNotExist:
            return Response({'detail': 'Rasm topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        image.image.delete(save=False)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin — Fields'])
class AdminFieldAmenityView(APIView):
    """Qulayliklar ro'yxati va qo'shish."""
    permission_classes = [IsAdminRole]

    def get(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FieldAmenitySerializer(field.amenities.all(), many=True).data)

    def post(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FieldAmenityWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(field=field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin — Fields'])
class AdminFieldAmenityDeleteView(APIView):
    """Qulaylikni o'chirish."""
    permission_classes = [IsAdminRole]

    def delete(self, request, pk, amenity_id):
        try:
            amenity = FieldAmenity.objects.get(pk=amenity_id, field_id=pk)
        except FieldAmenity.DoesNotExist:
            return Response({'detail': 'Qulaylik topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        amenity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Slot Management ──────────────────────────────────────────────────────────

@extend_schema(
    tags=['Slots'],
    parameters=[
        OpenApiParameter('date', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                         description='Sana (YYYY-MM-DD)'),
    ]
)
class AdminSlotListView(APIView):
    """Maydon slotlarini ko'rish va generatsiya qilish."""
    permission_classes = [IsAdminRole]

    def get(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': '"date" parametri talab qilinadi.'}, status=400)

        try:
            from datetime import datetime
            slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Noto\'g\'ri sana formati.'}, status=400)

        from apps.fields.utils import generate_slots_for_field_date
        slots = generate_slots_for_field_date(field, slot_date)
        return Response(TimeSlotSerializer(slots, many=True).data)


@extend_schema(tags=['Slots'])
class AdminSlotToggleView(APIView):
    """Slotni faol/nofaol qilish."""
    permission_classes = [IsAdminRole]

    def patch(self, request, slot_id):
        try:
            slot = TimeSlot.objects.get(pk=slot_id)
        except TimeSlot.DoesNotExist:
            return Response({'detail': 'Slot topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if slot.is_booked:
            return Response(
                {'detail': 'Band bo\'lgan slotni o\'zgartirib bo\'lmaydi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        slot.is_active = not slot.is_active
        slot.save(update_fields=['is_active'])
        return Response(TimeSlotSerializer(slot).data)


@extend_schema(tags=['Admin — Fields'])
class AdminSubscriptionView(APIView):
    """Maydon obunasini yangilash (+1 oy qo'shish)."""
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        from datetime import date
        from dateutil.relativedelta import relativedelta

        today = date.today()
        # Agar obuna tugagan bo'lsa — bugundan boshlanadi
        if not field.subscription_end or field.subscription_end < today:
            field.subscription_start = today
            field.subscription_end = today + relativedelta(months=1)
        else:
            field.subscription_end = field.subscription_end + relativedelta(months=1)

        field.is_subscription_active = True
        field.save(update_fields=['subscription_start', 'subscription_end', 'is_subscription_active'])

        return Response({
            'detail': 'Obuna 1 oyga uzaytirildi.',
            'subscription_start': str(field.subscription_start),
            'subscription_end': str(field.subscription_end),
        })
