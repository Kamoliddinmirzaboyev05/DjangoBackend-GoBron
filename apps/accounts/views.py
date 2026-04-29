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


@extend_schema(
    tags=['Auth'],
    request=MagicTokenSerializer,
    responses={200: UserSerializer}
)
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
            
            # Token yaroqliligini tekshirish
            if not magic_token.is_valid:
                if magic_token.is_expired:
                    error_msg = 'Token muddati tugagan. Botdan yangi link oling.'
                elif magic_token.usage_count >= magic_token.max_usage:
                    error_msg = 'Token ishlatish limiti tugagan. Botdan yangi link oling.'
                else:
                    error_msg = 'Token yaroqsiz'
                
                return Response({
                    'error': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Tokenni ishlatish
            if not magic_token.use_token():
                return Response({
                    'error': 'Token ishlatishda xatolik'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # JWT tokenlar yaratish
            user = magic_token.user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Muvaffaqiyatli autentifikatsiya',
                'user': UserSerializer(user, context={'request': request}).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'token_info': {
                    'usage_count': magic_token.usage_count,
                    'max_usage': magic_token.max_usage,
                    'expires_at': magic_token.expires_at.isoformat(),
                    'remaining_uses': magic_token.max_usage - magic_token.usage_count
                }
            }, status=status.HTTP_200_OK)
            
        except MagicToken.DoesNotExist:
            return Response({
                'error': 'Token topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Auth'],
    responses={200: UserSerializer}
)
class WebAuthView(APIView):
    """Web sayt uchun Magic Token autentifikatsiya (GET method)"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token')
        
        if not token:
            return Response({
                'error': 'Token talab qilinadi',
                'redirect': False
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            magic_token = MagicToken.objects.get(token=token)
            
            # Token yaroqliligini tekshirish
            if not magic_token.is_valid:
                if magic_token.is_expired:
                    error_msg = 'Token muddati tugagan. Botdan yangi link oling.'
                elif magic_token.usage_count >= magic_token.max_usage:
                    error_msg = 'Token ishlatish limiti tugagan. Botdan yangi link oling.'
                else:
                    error_msg = 'Token yaroqsiz'
                
                return Response({
                    'error': error_msg,
                    'redirect': False,
                    'expired': True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Tokenni ishlatish (usage_count ni oshirish)
            if not magic_token.use_token():
                return Response({
                    'error': 'Token ishlatishda xatolik',
                    'redirect': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # JWT tokenlar yaratish
            user = magic_token.user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Muvaffaqiyatli autentifikatsiya',
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'full_name': user.full_name,
                    'user_role': user.user_role,
                    'telegram_id': user.telegram_id,
                    'is_phone_verified': user.is_phone_verified,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'token_info': {
                    'usage_count': magic_token.usage_count,
                    'max_usage': magic_token.max_usage,
                    'expires_at': magic_token.expires_at.isoformat(),
                    'remaining_uses': magic_token.max_usage - magic_token.usage_count
                },
                'redirect': True
            }, status=status.HTTP_200_OK)
            
        except MagicToken.DoesNotExist:
            return Response({
                'error': 'Token topilmadi. Botdan yangi link oling.',
                'redirect': False
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
        # Swagger schema generation uchun
        if getattr(self, 'swagger_fake_view', False):
            return Stadium.objects.none()
            
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
        # Swagger schema generation uchun
        if getattr(self, 'swagger_fake_view', False):
            return Stadium.objects.none()
            
        if self.request.user.is_owner:
            return Stadium.objects.filter(owner=self.request.user)
        else:
            return Stadium.objects.filter(is_active=True)


@extend_schema(
    tags=['Debug'],
    responses={200: UserSerializer}
)
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
