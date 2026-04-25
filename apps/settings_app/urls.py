from django.urls import path
from .views import (
    AdminBookingListView,
    AdminBookingConfirmView,
    AdminBookingRejectView,
    AdminBookingManualCreateView,
    AdminStatsView,
    AdminFieldListCreateView,
    AdminFieldDetailView,
    AdminFieldImageUploadView,
    AdminFieldImageDeleteView,
    AdminFieldAmenityView,
    AdminFieldAmenityDeleteView,
    AdminSlotListView,
    AdminSlotToggleView,
    AdminSubscriptionView,
)

urlpatterns = [
    # Bronlar
    path('bookings/', AdminBookingListView.as_view(), name='admin-booking-list'),
    path('bookings/manual/', AdminBookingManualCreateView.as_view(), name='admin-booking-manual'),
    path('bookings/<int:pk>/confirm/', AdminBookingConfirmView.as_view(), name='admin-booking-confirm'),
    path('bookings/<int:pk>/reject/', AdminBookingRejectView.as_view(), name='admin-booking-reject'),

    # Statistika
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),

    # Maydonlar
    path('fields/', AdminFieldListCreateView.as_view(), name='admin-field-list-create'),
    path('fields/<int:pk>/', AdminFieldDetailView.as_view(), name='admin-field-detail'),
    path('fields/<int:pk>/images/', AdminFieldImageUploadView.as_view(), name='admin-field-images'),
    path('fields/<int:pk>/images/<int:img_id>/', AdminFieldImageDeleteView.as_view(), name='admin-field-image-delete'),
    path('fields/<int:pk>/amenities/', AdminFieldAmenityView.as_view(), name='admin-field-amenities'),
    path('fields/<int:pk>/amenities/<int:amenity_id>/', AdminFieldAmenityDeleteView.as_view(), name='admin-field-amenity-delete'),

    # Slotlar
    path('fields/<int:pk>/slots/', AdminSlotListView.as_view(), name='admin-slot-list'),
    path('slots/<int:slot_id>/toggle/', AdminSlotToggleView.as_view(), name='admin-slot-toggle'),

    # Obuna
    path('fields/<int:pk>/subscription/extend/', AdminSubscriptionView.as_view(), name='admin-subscription-extend'),
]
