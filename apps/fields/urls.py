from django.urls import path
from .views import (
    FootballFieldListView,
    FootballFieldDetailView,
    FieldSlotsView,
    FieldAvailableDatesView,
)

urlpatterns = [
    path('', FootballFieldListView.as_view(), name='field-list'),
    path('<int:pk>/', FootballFieldDetailView.as_view(), name='field-detail'),
    path('<int:pk>/slots/', FieldSlotsView.as_view(), name='field-slots'),
    path('<int:pk>/available-dates/', FieldAvailableDatesView.as_view(), name='field-available-dates'),
]
