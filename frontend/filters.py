import django_filters
from API.models import QueryJob

from django_filters import IsoDateTimeFilter, CharFilter


class QueryFilter(django_filters.FilterSet):

    class Meta:

        model = QueryJob

        fields = {
            
            'name': ['icontains']
           
            }

