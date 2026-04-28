from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from .models import CustomUser, MagicToken, Stadium
from .serializers import (
    UserSerializer,
    MagicTokenSerializer,
    StadiumSerializer,
    CustomTokenObtainPairSerializer,
)


@extend_schema(tags=['Auth'])
class VerifyMagicTokenView(APIView):
    """Magic Token orqali autentifikatsiya"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'Token talab qilinadi'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            magic_token = MagicToken.objects.get(token=token)
            
            if not magic_token.is_valid:
                return Response({
                    'error': 'Token yaroqsiz yoki muddati tugagan'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Tokenni ishlatilgan deb belgilash
            magic_token.is_used = True
            magic_token.save()
            
            # JWT tokenlar yaratish
            user = magic_token.user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Muvaffaqiyatli autentifikatsiya',
                'user': UserSerializer(user, context={'request': request}).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            
        except MagicToken.DoesNotExist:
            return Response({
                'error': 'Token topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """Foydalanuvchi profili"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Auth'])
class LoginView(TokenObtainPairView):
    """JWT token bilan kirish (fallback)"""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Stadiums'])
class StadiumListCreateView(generics.ListCreateAPIView):
    """Stadionlar ro'yxati va yaratish"""
    serializer_class = StadiumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_owner:
            # Maydon egasi faqat o'z stadionlarini ko'radi
            return Stadium.objects.filter(owner=self.request.user)
        else:
            # Futbolchilar barcha faol stadionlarni ko'radi
            return Stadium.objects.filter(is_active=True)

    def perform_create(self, serializer):
        if not self.request.user.is_owner:
            raise PermissionError("Faqat maydon egalari stadion yarata oladi")
        serializer.save(owner=self.request.user)


@extend_schema(tags=['Stadiums'])
class StadiumDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Stadion tafsilotlari"""
    serializer_class = StadiumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_owner:
            return Stadium.objects.filter(owner=self.request.user)
        else:
            return Stadium.objects.filter(is_active=True)


@extend_schema(tags=['Debug'])
class UserStatsView(APIView):
    """Foydalanuvchi statistikasi (debug uchun)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        stats = {
            'user_info': UserSerializer(user, context={'request': request}).data,
            'magic_tokens_count': MagicToken.objects.filter(user=user).count(),
            'active_tokens_count': MagicToken.objects.filter(
                user=user, 
                is_used=False,
                expires_at__gt=timezone.now()
            ).count(),
        }
        
        if user.is_owner:
            stats['stadiums_count'] = Stadium.objects.filter(owner=user).count()
        
        return Response(stats)
