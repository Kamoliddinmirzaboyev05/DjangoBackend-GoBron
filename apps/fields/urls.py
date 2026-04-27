from django.urls import path
from .views import (
    FootballFieldListView,
    FootballFieldDetailView,
    FieldSlotsView,
    FieldAvailableDatesView,
    SlotDetailView,
    MyFootballFieldsListView,
    MyFootballFieldDetailView,
    MyFootballFieldCreateView,
    FieldImageDeleteView,
    FieldImageUploadView,
)

urlpatterns = [
    path('', FootballFieldListView.as_view(), name='field-list'),
    path('my-fields/', MyFootballFieldsListView.as_view(), name='my-fields-list'),
    path('my-fields/create/', MyFootballFieldCreateView.as_view(), name='my-field-create'),
    path('my-fields/<int:pk>/', MyFootballFieldDetailView.as_view(), name='my-field-detail'),
    path('my-fields/upload-images/', FieldImageUploadView.as_view(), name='my-field-upload-images'),
    path('<int:pk>/', FootballFieldDetailView.as_view(), name='field-detail'),
    path('<int:pk>/slots/', FieldSlotsView.as_view(), name='field-slots'),
    path('<int:pk>/available-dates/', FieldAvailableDatesView.as_view(), name='field-available-dates'),
    path('slots/<int:slot_id>/', SlotDetailView.as_view(), name='slot-detail'),
    path('images/<int:pk>/', FieldImageDeleteView.as_view(), name='field-image-delete'),
]
