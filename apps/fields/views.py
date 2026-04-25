from datetime import datetime, date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import FootballFieldFilter
from .models import FootballField, TimeSlot
from .serializers import (
    FootballFieldListSerializer,
    FootballFieldDetailSerializer,
    TimeSlotSerializer,
)
from .utils import generate_slots_for_field_date, get_available_dates


@extend_schema(tags=['Fields'])
class FootballFieldListView(generics.ListAPIView):
    """Barcha faol futbol maydonlari ro'yxati."""
    permission_classes = [AllowAny]
    serializer_class = FootballFieldListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FootballFieldFilter
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['price_per_hour', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return FootballField.objects.filter(is_active=True).prefetch_related(
            'images', 'amenities'
        )


@extend_schema(tags=['Fields'])
class FootballFieldDetailView(generics.RetrieveAPIView):
    """Bitta futbol maydoni tafsilotlari."""
    permission_classes = [AllowAny]
    serializer_class = FootballFieldDetailSerializer
    queryset = FootballField.objects.filter(is_active=True).prefetch_related(
        'images', 'amenities'
    )


@extend_schema(
    tags=['Slots'],
    parameters=[
        OpenApiParameter(
            name='date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Sana (YYYY-MM-DD). Ko\'rsatilmasa bugungi kun.',
        )
    ],
)
class FieldSlotsView(APIView):
    """
    Maydon uchun berilgan sanadagi slotlarni ko'rish.
    Agar slotlar mavjud bo'lmasa avtomatik generatsiya qilinadi.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk, is_active=True)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date')
        if date_str:
            try:
                slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Noto\'g\'ri sana formati. YYYY-MM-DD ishlatilsin.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            slot_date = date.today()

        # Ruxsat etilgan sanalar oralig'ini tekshirish
        allowed_dates = get_available_dates(field)
        if slot_date not in allowed_dates:
            return Response(
                {
                    'detail': (
                        f'Bu maydon faqat {field.advance_booking_days} kun oldindan '
                        f'bron qilishga ruxsat beradi.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        slots = generate_slots_for_field_date(field, slot_date)
        serializer = TimeSlotSerializer(slots, many=True)
        return Response({
            'field_id': field.id,
            'field_name': field.name,
            'date': str(slot_date),
            'price_per_hour': str(field.price_per_hour),
            'advance_booking_days': field.advance_booking_days,
            'available_dates': [str(d) for d in allowed_dates],
            'slots': serializer.data,
        })


@extend_schema(tags=['Slots'])
class FieldAvailableDatesView(APIView):
    """Maydon uchun bron qilish mumkin bo'lgan sanalar ro'yxati."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            field = FootballField.objects.get(pk=pk, is_active=True)
        except FootballField.DoesNotExist:
            return Response({'detail': 'Maydon topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        allowed_dates = get_available_dates(field)
        return Response({
            'field_id': field.id,
            'field_name': field.name,
            'advance_booking_days': field.advance_booking_days,
            'available_dates': [str(d) for d in allowed_dates],
        })
