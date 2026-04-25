from django.urls import path
from .views import (
    FootballFieldListView,
    FootballFieldDetailView,
    FieldSlotsView,
    FieldAvailableDatesView,
    MyFootballFieldView,
    FieldImageDeleteView,
    FieldImageUploadView,
)

urlpatterns = [
    path('', FootballFieldListView.as_view(), name='field-list'),
    path('my-field/', MyFootballFieldView.as_view(), name='my-field'),
    path('my-field/upload-images/', FieldImageUploadView.as_view(), name='my-field-upload-images'),
    path('<int:pk>/', FootballFieldDetailView.as_view(), name='field-detail'),
    path('<int:pk>/slots/', FieldSlotsView.as_view(), name='field-slots'),
    path('<int:pk>/available-dates/', FieldAvailableDatesView.as_view(), name='field-available-dates'),
    path('images/<int:pk>/', FieldImageDeleteView.as_view(), name='field-image-delete'),
]
