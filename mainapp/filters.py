import django_filters
from mainapp.models import *


class TourFilter(django_filters.FilterSet):
    class Meta:
        model = Tour
        fields = {
            'name': ['icontains']
        }