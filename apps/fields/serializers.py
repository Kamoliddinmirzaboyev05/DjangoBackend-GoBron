from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import FootballField, FieldImage, FieldAmenity, TimeSlot


class FieldImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FieldImage
        fields = ('id', 'image', 'image_url', 'order')
        extra_kwargs = {'image': {'write_only': True}}

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class FieldAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldAmenity
        fields = ('id', 'name', 'icon')


class FootballFieldListSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    amenities = FieldAmenitySerializer(many=True, read_only=True)
    images_count = serializers.SerializerMethodField()
    subscription_valid = serializers.BooleanField(
        source='subscription_is_valid', read_only=True
    )

    class Meta:
        model = FootballField
        fields = (
            'id', 'name', 'address', 'city', 'location_url', 'phone',
            'price_per_hour', 'opening_time', 'closing_time',
            'advance_booking_days', 'is_active', 'subscription_valid',
            'cover_image_url', 'amenities', 'images_count', 'created_at',
        )

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    @extend_schema_field(serializers.IntegerField())
    def get_images_count(self, obj):
        return obj.images.count()


class FootballFieldDetailSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    images = FieldImageSerializer(many=True, read_only=True)
    amenities = FieldAmenitySerializer(many=True, read_only=True)
    subscription_valid = serializers.BooleanField(
        source='subscription_is_valid', read_only=True
    )

    class Meta:
        model = FootballField
        fields = (
            'id', 'name', 'description', 'address', 'city', 'location_url', 'phone',
            'price_per_hour', 'opening_time', 'closing_time',
            'advance_booking_days', 'is_active', 'subscription_valid',
            'cover_image', 'cover_image_url',
            'images', 'amenities', 'created_at', 'updated_at',
        )
        extra_kwargs = {'cover_image': {'write_only': True, 'required': False}}

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None


class FootballFieldWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballField
        fields = (
            'id', 'owner', 'name', 'description', 'address', 'city',
            'location_url', 'phone', 'price_per_hour',
            'opening_time', 'closing_time', 'advance_booking_days',
            'is_active', 'cover_image',
            'subscription_start', 'subscription_end', 'is_subscription_active',
        )

    def validate(self, attrs):
        opening = attrs.get('opening_time', getattr(self.instance, 'opening_time', None))
        closing = attrs.get('closing_time', getattr(self.instance, 'closing_time', None))
        if opening and closing and opening == closing:
            raise serializers.ValidationError(
                {'closing_time': 'Yopilish vaqti ochilish vaqtidan farq qilishi kerak.'}
            )
        return attrs


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = (
            'id', 'field', 'date', 'start_time', 'end_time',
            'is_active', 'is_booked',
        )
        read_only_fields = ('id', 'is_booked')


class TimeSlotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ('id', 'field', 'date', 'start_time', 'end_time', 'is_active', 'is_booked')
        read_only_fields = ('id', 'field', 'date', 'start_time', 'end_time', 'is_booked')


class FieldImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldImage
        fields = ('id', 'image', 'order')


class FieldAmenityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldAmenity
        fields = ('id', 'name', 'icon')
