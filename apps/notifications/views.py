from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Admin — Notifications'])
class AdminNotificationListView(generics.ListAPIView):
    """O'qilmagan bildirishnomalar ro'yxati."""
    permission_classes = [IsAdminRole]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Swagger schema generation uchun
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
            
        return Notification.objects.filter(
            recipient=self.request.user,
            is_read=False,
        ).select_related('booking', 'booking__field', 'booking__user')


@extend_schema(tags=['Admin — Notifications'])
class AdminNotificationMarkReadView(APIView):
    """Bildirishnomani o'qilgan deb belgilash."""
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return Response(NotificationSerializer(n).data)


@extend_schema(tags=['Admin — Notifications'])
class AdminNotificationMarkAllReadView(APIView):
    """Barcha bildirishnomalarni o'qilgan deb belgilash."""
    permission_classes = [IsAdminRole]

    def patch(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({'detail': f'{count} ta bildirishnoma o\'qildi.'})
