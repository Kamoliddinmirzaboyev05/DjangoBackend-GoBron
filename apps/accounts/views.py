from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError

from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish."""
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserProfileSerializer(user, context={'request': request}).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Auth'])
class LoginView(TokenObtainPairView):
    """Kirish — JWT token olish."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Auth'])
class LogoutView(APIView):
    """Chiqish — refresh tokenni blacklistga qo'shish."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'detail': 'Refresh token talab qilinadi.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'detail': 'Muvaffaqiyatli chiqildi.'},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {'detail': 'Token yaroqsiz yoki muddati o\'tgan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """Profil ko'rish va yangilash."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
