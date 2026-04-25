import django_filters
from .models import FootballField


class FootballFieldFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price_per_hour', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price_per_hour', lookup_expr='lte')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = FootballField
        fields = ['city', 'price_min', 'price_max', 'name', 'is_active']
