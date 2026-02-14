"""
Tests for Booking model.
"""

from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from apps.bookings.models import Booking, BookingStatus


@pytest.mark.django_db
class TestBookingModel:
    """Tests for the Booking model."""
    
    def test_create_booking(self, user, venue):
        """Test creating a booking."""
        booking = Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        assert booking.user == user
        assert booking.venue == venue
        assert booking.status == BookingStatus.PENDING
        assert booking.total_price is not None
    
    def test_price_calculation_2_hours(self, user, venue):
        """Test price calculation for 2-hour booking."""
        # venue.price_per_hour = 100000
        booking = Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(12, 0),  # 2 hours
        )
        
        expected_price = venue.price_per_hour * 2
        assert booking.total_price == expected_price
    
    def test_price_calculation_half_hour(self, user, venue):
        """Test price calculation for half-hour booking."""
        booking = Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(10, 30),  # 0.5 hours
        )
        
        expected_price = venue.price_per_hour * Decimal("0.5")
        assert booking.total_price == expected_price
    
    def test_duration_hours_property(self, booking):
        """Test duration_hours property."""
        # booking is 10:00 - 12:00 = 2 hours
        assert booking.duration_hours == 2.0
    
    def test_can_cancel_pending(self, booking):
        """Test can_cancel for pending booking."""
        assert booking.status == BookingStatus.PENDING
        assert booking.can_cancel is True
    
    def test_can_cancel_confirmed(self, confirmed_booking):
        """Test can_cancel for confirmed booking."""
        assert confirmed_booking.status == BookingStatus.CONFIRMED
        assert confirmed_booking.can_cancel is True
    
    def test_cannot_cancel_cancelled(self, cancelled_booking):
        """Test can_cancel for already cancelled booking."""
        assert cancelled_booking.status == BookingStatus.CANCELLED
        assert cancelled_booking.can_cancel is False
    
    def test_cannot_cancel_completed(self, completed_booking):
        """Test can_cancel for completed booking."""
        assert completed_booking.status == BookingStatus.COMPLETED
        assert completed_booking.can_cancel is False
    
    def test_cancel_method(self, booking):
        """Test cancel method changes status."""
        assert booking.status == BookingStatus.PENDING
        
        result = booking.cancel()
        
        assert result is True
        booking.refresh_from_db()
        assert booking.status == BookingStatus.CANCELLED
    
    def test_cancel_method_fails_for_completed(self, completed_booking):
        """Test cancel method returns False for completed booking."""
        result = completed_booking.cancel()
        
        assert result is False
        completed_booking.refresh_from_db()
        assert completed_booking.status == BookingStatus.COMPLETED
    
    def test_str_representation(self, booking):
        """Test string representation."""
        expected = f"{booking.venue.name} - {booking.booking_date} ({booking.start_time}-{booking.end_time})"
        assert str(booking) == expected
    
    def test_booking_ordering(self, user, venue, db):
        """Test bookings are ordered by date and time descending."""
        booking1 = Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
        )
        booking2 = Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=date.today() + timedelta(days=2),
            start_time=time(10, 0),
            end_time=time(11, 0),
        )
        
        bookings = list(Booking.objects.all())
        
        # Later date first
        assert bookings[0] == booking2
        assert bookings[1] == booking1
