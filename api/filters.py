"""
Custom filters for API endpoints
"""
from django_filters import rest_framework as filters
from main.models import ClassifiedAd, Category


class ClassifiedAdFilter(filters.FilterSet):
    """
    Filter for classified ads
    """
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category_id = filters.NumberFilter(field_name='category__id')
    country_id = filters.NumberFilter(field_name='country__id')

    class Meta:
        model = ClassifiedAd
        fields = ['category', 'country', 'city', 'status', 'is_featured', 'is_urgent', 'negotiable']


class CategoryFilter(filters.FilterSet):
    """
    Filter for categories
    """
    section_type = filters.CharFilter(field_name='section_type')
    parent_id = filters.NumberFilter(field_name='parent__id')
    country_id = filters.NumberFilter(field_name='country__id')

    class Meta:
        model = Category
        fields = ['section_type', 'parent', 'country']
