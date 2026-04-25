from django.urls import path

from .views import (
    AdminNotificationListView,
    AdminNotificationMarkReadView,
    AdminNotificationMarkAllReadView,
)

urlpatterns = [
    path('notifications/', AdminNotificationListView.as_view(), name='admin-notifications'),
    path('notifications/read-all/', AdminNotificationMarkAllReadView.as_view(), name='admin-notifications-read-all'),
    path('notifications/<int:pk>/read/', AdminNotificationMarkReadView.as_view(), name='admin-notification-read'),
]
