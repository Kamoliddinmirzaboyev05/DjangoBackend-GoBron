from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.accounts.models import CustomUser
from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer


def _notify_admins(booking):
    admins = CustomUser.objects.filter(role='admin', is_active=True)
    notifications = [
        Notification(
            recipient=admin,
            booking=booking,
            message=(
                f'Yangi bron #{booking.pk}: {booking.client_name} '
                f'— {booking.field.name}, {booking.date} '
                f'{booking.start_time:%H:%M}-{booking.end_time:%H:%M}.'
            ),
        )
        for admin in admins
    ]
    Notification.objects.bulk_create(notifications)


@extend_schema(tags=['Bookings'])
class BookingCreateView(generics.CreateAPIView):
    """Slot uchun bron so'rovi yuborish."""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        _notify_admins(booking)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        booking = serializer.instance
        detail = BookingSerializer(booking, context={'request': request})
        return Response(detail.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Bookings'])
class MyBookingsView(generics.ListAPIView):
    """Mening bronlarim ro'yxati."""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    queryset = Booking.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related('field', 'user', 'slot')
            .order_by('-created_at')
        )


@extend_schema(
    tags=['Bookings'],
    responses={200: OpenApiResponse(description='Bron bekor qilindi.')}
)
class BookingCancelView(APIView):
    """Bronni bekor qilish (faqat pending holatda)."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user)
        except Booking.DoesNotExist:
            return Response({'detail': 'Bron topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != 'pending':
            return Response(
                {'detail': f'Faqat kutilayotgan bronni bekor qilish mumkin. Holat: "{booking.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = 'cancelled'
        booking.save(update_fields=['status'])

        if booking.slot:
            booking.slot.is_booked = False
            booking.slot.save(update_fields=['is_booked'])

        return Response({'detail': 'Bron bekor qilindi.'}, status=status.HTTP_200_OK)
