"""
Filters for venues app.
"""

from django_filters import rest_framework as filters

from .models import Venue


class VenueFilter(filters.FilterSet):
    """
    Filter set for Venue model.
    Supports filtering by price range.
    """
    
    min_price = filters.NumberFilter(
        field_name="price_per_hour",
        lookup_expr="gte",
        label="Minimum price per hour",
    )
    max_price = filters.NumberFilter(
        field_name="price_per_hour",
        lookup_expr="lte",
        label="Maximum price per hour",
    )
    
    class Meta:
        model = Venue
        fields = ["min_price", "max_price"]
