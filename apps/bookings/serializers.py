"""
Serializers for bookings app.
"""

from datetime import date, time

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from apps.venues.serializers import VenueListSerializer

from .models import Booking, BookingStatus


class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer for booking list view.
    """
    
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    
    class Meta:
        model = Booking
        fields = (
            "id",
            "venue",
            "venue_name",
            "booking_date",
            "start_time",
            "end_time",
            "total_price",
            "status",
            "created_at",
        )


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for booking detail view.
    """
    
    venue = VenueListSerializer(read_only=True)
    duration_hours = serializers.FloatField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = (
            "id",
            "venue",
            "booking_date",
            "start_time",
            "end_time",
            "total_price",
            "status",
            "duration_hours",
            "can_cancel",
            "created_at",
            "updated_at",
        )


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a booking.
    """
    
    class Meta:
        model = Booking
        fields = (
            "venue",
            "booking_date",
            "start_time",
            "end_time",
        )
    
    def validate_booking_date(self, value):
        """Ensure booking date is not in the past."""
        if value < date.today():
            raise serializers.ValidationError("Booking date cannot be in the past.")
        return value
    
    def validate(self, attrs):
        """
        Validate booking time and availability.
        """
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        venue = attrs.get("venue")
        booking_date = attrs.get("booking_date")
        
        # Validate end time is after start time
        if end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })
        
        # Validate booking hours
        start_hour = getattr(settings, "BOOKING_START_HOUR", 9)
        end_hour = getattr(settings, "BOOKING_END_HOUR", 22)
        
        min_time = time(hour=start_hour)
        max_time = time(hour=end_hour)
        
        if start_time < min_time or end_time > max_time:
            raise serializers.ValidationError({
                "start_time": f"Booking time must be between {start_hour}:00 and {end_hour}:00."
            })
        
        # Check venue availability (prevent double booking)
        # Check for overlapping bookings
        existing_bookings = Booking.objects.filter(
            venue=venue,
            booking_date=booking_date,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        )
        
        for booking in existing_bookings:
            # Check if times overlap
            # Two time ranges overlap if NOT (one ends before the other starts)
            if not (end_time <= booking.start_time or start_time >= booking.end_time):
                raise serializers.ValidationError({
                    "start_time": "This time slot is already booked."
                })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create booking with user from request.
        Uses atomic transaction to prevent race conditions with double bookings.
        """
        validated_data["user"] = self.context["request"].user
        
        # Re-check availability within transaction using select_for_update
        venue = validated_data["venue"]
        booking_date = validated_data["booking_date"]
        start_time = validated_data["start_time"]
        end_time = validated_data["end_time"]
        
        # Lock the venue's bookings for update to prevent race conditions
        existing_bookings = Booking.objects.select_for_update().filter(
            venue=venue,
            booking_date=booking_date,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        )
        
        for booking in existing_bookings:
            if not (end_time <= booking.start_time or start_time >= booking.end_time):
                raise serializers.ValidationError({
                    "start_time": "This time slot was just booked by another user."
                })
        
        return super().create(validated_data)


class BookingCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling a booking (no fields needed).
    """
    pass
