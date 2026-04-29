from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    VerifyMagicTokenView,
    WebAuthView,
    ProfileView,
    LoginView,
    StadiumListCreateView,
    StadiumDetailView,
    UserStatsView,
)

urlpatterns = [
    # Magic Token Auth
    path('verify-token/', VerifyMagicTokenView.as_view(), name='verify-magic-token'),
    path('web-auth/', WebAuthView.as_view(), name='web-auth'),
    
    # User Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # JWT Auth (fallback)
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Stadiums
    path('stadiums/', StadiumListCreateView.as_view(), name='stadium-list'),
    path('stadiums/<int:pk>/', StadiumDetailView.as_view(), name='stadium-detail'),
    
    # Debug
    path('stats/', UserStatsView.as_view(), name='user-stats'),
]
