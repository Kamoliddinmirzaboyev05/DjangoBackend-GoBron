from datetime import datetime, date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .filters import FootballFieldFilter
from .models import FootballField, TimeSlot, FieldImage
from .serializers import (
    FootballFieldListSerializer,
    FootballFieldDetailSerializer,
    FootballFieldWriteSerializer,
    FieldImageSerializer,
    TimeSlotSerializer,
)
from .utils import generate_slots_for_field_date, get_available_dates
from apps.accounts.permissions import IsAdminRole


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


@extend_schema(tags=['Fields Admin'])
class MyFootballFieldView(generics.RetrieveUpdateAPIView):
    """Admin o'ziga tegishli maydonni ko'rishi va tahrirlashi (rasm yuklash bilan)."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = FootballFieldWriteSerializer

    def get_object(self):
        try:
            return FootballField.objects.get(owner=self.request.user)
        except FootballField.DoesNotExist:
            return Response(
                {'detail': 'Sizga biriktirilgan maydon topilmadi.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FootballFieldDetailSerializer
        return FootballFieldWriteSerializer


@extend_schema(tags=['Fields Admin'])
class FieldImageDeleteView(generics.DestroyAPIView):
    """Admin maydonidagi rasmni o'chirishi."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = FieldImage.objects.all()
    serializer_class = FieldImageSerializer

    def get_queryset(self):
        return self.queryset.filter(field__owner=self.request.user)


@extend_schema(tags=['Fields Admin'])
class FieldImageUploadView(APIView):
    """Admin o'z maydoniga rasm(lar) yuklashi uchun maxsus endpoint."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'},
                        'description': 'Bir yoki bir nechta rasm fayllari'
                    }
                }
            }
        },
        responses={201: FieldImageSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):
        try:
            field = FootballField.objects.get(owner=request.user)
        except FootballField.DoesNotExist:
            return Response(
                {'detail': 'Sizga biriktirilgan maydon topilmadi.'},
                status=status.HTTP_404_NOT_FOUND
            )

        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'detail': 'Hech qanday rasm yuborilmadi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_images = []
        for img_file in images:
            img_obj = FieldImage.objects.create(field=field, image=img_file)
            created_images.append(img_obj)

        serializer = FieldImageSerializer(created_images, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
