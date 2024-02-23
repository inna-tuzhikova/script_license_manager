from django_filters import CharFilter
from django_filters.rest_framework import FilterSet

from .models import Script


class ScriptFilter(FilterSet):
    """Filtering scripts requests with get params"""

    without_tag = CharFilter(field_name='tags__name', exclude=True)
    tag = CharFilter(field_name='tags__name')

    class Meta:
        model = Script
        fields = ['category', 'enabled', 'is_active', 'tag', 'without_tag']
