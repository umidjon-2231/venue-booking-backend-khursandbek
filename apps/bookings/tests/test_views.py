"""
Tests for booking views.
"""

from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from rest_framework import status

from apps.bookings.models import Booking, BookingStatus


@pytest.mark.django_db
class TestBookingListCreateView:
    """Tests for booking list and create endpoint."""
    
    url = "/api/bookings/"
    
    def test_list_bookings_requires_auth(self, api_client):
        """Test that listing bookings requires authentication."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_own_bookings(self, authenticated_client, booking, confirmed_booking):
        """Test listing authenticated user's bookings."""
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
    
    def test_list_only_own_bookings(self, authenticated_client, booking, user2, venue, db):
        """Test that user only sees their own bookings."""
        # Create booking for another user
        other_booking = Booking.objects.create(
            user=user2,
            venue=venue,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        booking_ids = [b["id"] for b in response.data["results"]]
        
        assert booking.id in booking_ids
        assert other_booking.id not in booking_ids
    
    def test_create_booking_success(self, authenticated_client, venue):
        """Test creating a booking successfully."""
        tomorrow = date.today() + timedelta(days=1)
        
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "14:00",
            "end_time": "16:00",
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["venue"]["id"] == venue.id
        assert response.data["status"] == BookingStatus.PENDING
        # 2 hours * 100000 = 200000
        assert Decimal(response.data["total_price"]) == Decimal("200000.00")
    
    def test_create_booking_requires_auth(self, api_client, venue):
        """Test that creating booking requires authentication."""
        tomorrow = date.today() + timedelta(days=1)
        
        response = api_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "14:00",
            "end_time": "16:00",
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_booking_past_date_fails(self, authenticated_client, venue):
        """Test that booking in the past fails."""
        yesterday = date.today() - timedelta(days=1)
        
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": yesterday.isoformat(),
            "start_time": "14:00",
            "end_time": "16:00",
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for field in error details (custom exception handler wraps errors)
        error_details = response.data.get("error", {}).get("details", response.data)
        assert "booking_date" in error_details
    
    def test_create_booking_end_before_start_fails(self, authenticated_client, venue):
        """Test that end time before start time fails."""
        tomorrow = date.today() + timedelta(days=1)
        
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "16:00",
            "end_time": "14:00",  # Before start
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_details = response.data.get("error", {}).get("details", response.data)
        assert "end_time" in error_details
    
    def test_create_booking_outside_hours_fails(self, authenticated_client, venue):
        """Test that booking outside allowed hours fails."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Before 9 AM
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "08:00",
            "end_time": "10:00",
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_details = response.data.get("error", {}).get("details", response.data)
        assert "start_time" in error_details
    
    def test_create_booking_after_10pm_fails(self, authenticated_client, venue):
        """Test that booking after 10 PM fails."""
        tomorrow = date.today() + timedelta(days=1)
        
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "21:00",
            "end_time": "23:00",  # After 22:00
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_booking_double_booking_fails(self, authenticated_client, venue, user, db):
        """Test that double booking is prevented."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create existing booking
        Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status=BookingStatus.CONFIRMED,
        )
        
        # Try to book overlapping time
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "11:00",  # Overlaps with 10-12
            "end_time": "13:00",
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_details = response.data.get("error", {}).get("details", response.data)
        assert "start_time" in error_details
        assert "already booked" in str(error_details.get("start_time", "")).lower()
    
    def test_create_booking_adjacent_time_succeeds(self, authenticated_client, venue, user, db):
        """Test that booking immediately after existing booking succeeds."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create existing booking
        Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status=BookingStatus.CONFIRMED,
        )
        
        # Book right after (12:00 - 14:00)
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "12:00",
            "end_time": "14:00",
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_cancelled_booking_slot_available(self, authenticated_client, venue, user, db):
        """Test that cancelled booking's slot is available."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create cancelled booking
        Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status=BookingStatus.CANCELLED,
        )
        
        # Should be able to book same time
        response = authenticated_client.post(self.url, {
            "venue": venue.id,
            "booking_date": tomorrow.isoformat(),
            "start_time": "10:00",
            "end_time": "12:00",
        })
        
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestBookingDetailView:
    """Tests for booking detail endpoint."""
    
    def get_url(self, booking_id):
        return f"/api/bookings/{booking_id}/"
    
    def test_get_booking_detail(self, authenticated_client, booking):
        """Test getting booking details."""
        response = authenticated_client.get(self.get_url(booking.id))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == booking.id
        assert "venue" in response.data
        assert "duration_hours" in response.data
        assert "can_cancel" in response.data
    
    def test_get_booking_not_found(self, authenticated_client):
        """Test getting non-existent booking."""
        response = authenticated_client.get(self.get_url(99999))
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cannot_get_other_users_booking(self, authenticated_client, user2, venue, db):
        """Test that user cannot access another user's booking."""
        other_booking = Booking.objects.create(
            user=user2,
            venue=venue,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        response = authenticated_client.get(self.get_url(other_booking.id))
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookingCancelView:
    """Tests for booking cancel endpoint."""
    
    def get_url(self, booking_id):
        return f"/api/bookings/{booking_id}/cancel/"
    
    def test_cancel_pending_booking(self, authenticated_client, booking):
        """Test cancelling a pending booking."""
        assert booking.status == BookingStatus.PENDING
        
        response = authenticated_client.patch(self.get_url(booking.id))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == BookingStatus.CANCELLED
        
        booking.refresh_from_db()
        assert booking.status == BookingStatus.CANCELLED
    
    def test_cancel_confirmed_booking(self, authenticated_client, confirmed_booking):
        """Test cancelling a confirmed booking."""
        response = authenticated_client.patch(self.get_url(confirmed_booking.id))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == BookingStatus.CANCELLED
    
    def test_cannot_cancel_completed_booking(self, authenticated_client, completed_booking):
        """Test that completed booking cannot be cancelled."""
        response = authenticated_client.patch(self.get_url(completed_booking.id))
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_cancel_already_cancelled(self, authenticated_client, cancelled_booking):
        """Test that already cancelled booking cannot be cancelled again."""
        response = authenticated_client.patch(self.get_url(cancelled_booking.id))
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_cancel_other_users_booking(self, authenticated_client, user2, venue, db):
        """Test that user cannot cancel another user's booking."""
        other_booking = Booking.objects.create(
            user=user2,
            venue=venue,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        response = authenticated_client.patch(self.get_url(other_booking.id))
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cancel_requires_auth(self, api_client, booking):
        """Test that cancelling requires authentication."""
        response = api_client.patch(self.get_url(booking.id))
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
