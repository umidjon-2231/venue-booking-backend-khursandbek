"""
Views for bookings app.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import BookingCancellationException
from core.permissions import IsOwner

from .models import Booking
from .serializers import (
    BookingCancelSerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingListSerializer,
)


class BookingListCreateView(generics.ListCreateAPIView):
    """
    List user's bookings or create a new booking.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's bookings."""
        return Booking.objects.filter(user=self.request.user).select_related("venue")
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookingCreateSerializer
        return BookingListSerializer
    
    @extend_schema(
        responses={200: BookingListSerializer(many=True)},
        summary="List My Bookings",
        description="Get all bookings for the authenticated user.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=BookingCreateSerializer,
        responses={
            201: BookingDetailSerializer,
            400: OpenApiResponse(description="Validation error or time slot not available"),
        },
        summary="Create Booking",
        description="Create a new booking. Checks venue availability and validates booking time.",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Return detailed response
        detail_serializer = BookingDetailSerializer(booking)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class BookingDetailView(generics.RetrieveAPIView):
    """
    Get booking details.
    """
    
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """Return only the current user's bookings."""
        return Booking.objects.filter(user=self.request.user).select_related("venue")
    
    @extend_schema(
        responses={200: BookingDetailSerializer},
        summary="Get Booking Details",
        description="Get detailed information about a specific booking.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingCancelView(APIView):
    """
    Cancel a booking.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=BookingCancelSerializer,
        responses={
            200: BookingDetailSerializer,
            400: OpenApiResponse(description="Booking cannot be cancelled"),
            404: OpenApiResponse(description="Booking not found"),
        },
        summary="Cancel Booking",
        description="Cancel a pending or confirmed booking. Completed or already cancelled bookings cannot be cancelled.",
    )
    def patch(self, request, pk):
        # Get booking
        try:
            booking = Booking.objects.get(pk=pk, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Check if booking can be cancelled
        if not booking.can_cancel:
            raise BookingCancellationException(
                "This booking cannot be cancelled. Only pending or confirmed bookings can be cancelled."
            )
        
        # Cancel booking
        booking.cancel()
        
        # Return updated booking
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
