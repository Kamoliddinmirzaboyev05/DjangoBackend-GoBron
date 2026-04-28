from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field

from .models import CustomUser, MagicToken, Stadium


class UserSerializer(serializers.ModelSerializer):
    """Foydalanuvchi serializer"""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'phone_number', 'telegram_id', 'user_role',
            'full_name', 'avatar_url', 'is_phone_verified',
            'telegram_username', 'date_joined'
        )
        read_only_fields = (
            'id', 'telegram_id', 'is_phone_verified', 'date_joined'
        )

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class MagicTokenSerializer(serializers.ModelSerializer):
    """Magic Token serializer"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = MagicToken
        fields = ('token', 'user', 'created_at', 'expires_at', 'is_used')
        read_only_fields = ('token', 'created_at', 'expires_at')


class StadiumSerializer(serializers.ModelSerializer):
    """Stadion serializer"""
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Stadium
        fields = (
            'id', 'owner', 'name', 'address', 'hourly_rate',
            'description', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token serializer"""
    username_field = 'phone_number'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone_number'] = user.phone_number
        token['user_role'] = user.user_role
        token['telegram_id'] = user.telegram_id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user, context={'request': self.context.get('request')}).data
        return data
