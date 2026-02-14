"""
Views for venues app.
"""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdminOrReadOnly

from .filters import VenueFilter
from .models import Venue
from .serializers import (
    AvailabilityRequestSerializer,
    VenueAvailabilitySerializer,
    VenueCreateUpdateSerializer,
    VenueDetailSerializer,
    VenueListSerializer,
)
from .services import get_available_time_slots


class VenueListView(generics.ListCreateAPIView):
    """
    List all active venues or create a new venue (admin only).
    
    GET: Returns paginated list of active venues with filtering and search.
    POST: Creates a new venue (admin only).
    """
    
    filterset_class = VenueFilter
    search_fields = ["name", "name_ru", "name_uz", "name_en"]
    ordering_fields = ["price_per_hour", "created_at", "name"]
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        Optimized queryset with prefetch for uploaded images.
        Uses select_related and prefetch_related to minimize DB queries.
        """
        return Venue.objects.prefetch_related("uploaded_images").all()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return VenueCreateUpdateSerializer
        return VenueListSerializer
    
    @method_decorator(cache_page(60))  # Cache for 1 minute
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="min_price",
                description="Minimum price per hour",
                type=float,
            ),
            OpenApiParameter(
                name="max_price",
                description="Maximum price per hour",
                type=float,
            ),
            OpenApiParameter(
                name="search",
                description="Search by venue name",
                type=str,
            ),
        ],
        responses={200: VenueListSerializer(many=True)},
        summary="List Venues",
        description="List all active venues with pagination, filtering, and search.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=VenueCreateUpdateSerializer,
        responses={201: VenueDetailSerializer},
        summary="Create Venue",
        description="Create a new venue (admin only).",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class VenueDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a venue.
    
    GET: Returns detailed venue information.
    PUT/PATCH: Updates venue (admin only).
    DELETE: Soft-deletes venue (admin only).
    """
    
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Optimized queryset with prefetch for uploaded images."""
        return Venue.objects.prefetch_related("uploaded_images").all()
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return VenueCreateUpdateSerializer
        return VenueDetailSerializer
    
    @method_decorator(cache_page(60))  # Cache for 1 minute
    @extend_schema(
        responses={200: VenueDetailSerializer},
        summary="Get Venue Details",
        description="Get detailed information about a specific venue.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=VenueCreateUpdateSerializer,
        responses={200: VenueDetailSerializer},
        summary="Update Venue",
        description="Update venue information (admin only).",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=VenueCreateUpdateSerializer,
        responses={200: VenueDetailSerializer},
        summary="Partial Update Venue",
        description="Partially update venue information (admin only).",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: None},
        summary="Delete Venue",
        description="Delete a venue (admin only). This is a soft delete.",
    )
    def delete(self, request, *args, **kwargs):
        venue = self.get_object()
        venue.deactivate()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VenueAvailabilityView(APIView):
    """
    Get available time slots for a venue on a specific date.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                description="Date to check availability (YYYY-MM-DD)",
                type=str,
                required=True,
            ),
        ],
        responses={200: VenueAvailabilitySerializer},
        summary="Get Venue Availability",
        description="Get available time slots for a specific venue on a given date.",
    )
    def get(self, request, pk):
        # Validate venue exists
        try:
            venue = Venue.objects.get(pk=pk)
        except Venue.DoesNotExist:
            return Response(
                {"error": "Venue not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Validate date parameter
        serializer = AvailabilityRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        check_date = serializer.validated_data["date"]
        
        # Get available time slots
        time_slots = get_available_time_slots(venue.id, check_date)
        
        return Response({
            "venue_id": venue.id,
            "date": check_date,
            "time_slots": time_slots,
        })
