from django.urls import path

from .views import BookingCreateView, MyBookingsView, BookingCancelView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('my/', MyBookingsView.as_view(), name='booking-my'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
]
