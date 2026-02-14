"""
Tests for venue views.
"""

from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from rest_framework import status

from apps.bookings.models import Booking, BookingStatus
from apps.venues.models import Venue


@pytest.mark.django_db
class TestVenueListView:
    """Tests for venue list endpoint."""
    
    url = "/api/venues/"
    
    def test_list_venues_public(self, api_client, venue, venue2):
        """Test listing venues is public (no auth required)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 2
    
    def test_list_excludes_inactive_venues(self, api_client, venue, inactive_venue):
        """Test that inactive venues are excluded from list."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        venue_ids = [v["id"] for v in response.data["results"]]
        
        assert venue.id in venue_ids
        assert inactive_venue.id not in venue_ids
    
    def test_pagination(self, api_client, db):
        """Test pagination returns 10 items per page."""
        # Create 15 venues
        for i in range(15):
            Venue.objects.create(
                name=f"Venue {i}",
                address=f"Address {i}",
                price_per_hour=Decimal("100000.00"),
            )
        
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10
        assert response.data["count"] == 15
        assert response.data["next"] is not None
    
    def test_filter_by_min_price(self, api_client, venue, venue2):
        """Test filtering by minimum price."""
        # venue: 100000, venue2: 200000
        response = api_client.get(self.url, {"min_price": 150000})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == venue2.id
    
    def test_filter_by_max_price(self, api_client, venue, venue2):
        """Test filtering by maximum price."""
        response = api_client.get(self.url, {"max_price": 150000})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == venue.id
    
    def test_filter_by_price_range(self, api_client, db):
        """Test filtering by price range."""
        Venue.objects.create(name="Cheap", address="Addr", price_per_hour=Decimal("50000"))
        Venue.objects.create(name="Medium", address="Addr", price_per_hour=Decimal("100000"))
        Venue.objects.create(name="Expensive", address="Addr", price_per_hour=Decimal("200000"))
        
        response = api_client.get(self.url, {"min_price": 75000, "max_price": 150000})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Medium"
    
    def test_search_by_name(self, api_client, venue, venue2):
        """Test searching by venue name."""
        response = api_client.get(self.url, {"search": "Test"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == venue.id
    
    def test_create_venue_requires_admin(self, authenticated_client):
        """Test that creating venue requires admin privileges."""
        response = authenticated_client.post(self.url, {
            "name": "New Venue",
            "address": "New Address",
            "price_per_hour": "100000.00",
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_venue_as_admin(self, admin_client):
        """Test that admin can create venue."""
        response = admin_client.post(self.url, {
            "name": "Admin Venue",
            "address": "Admin Address",
            "description": "Created by admin",
            "price_per_hour": "150000.00",
            "images": [],
            "amenities": ["WiFi"],
        }, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Venue.objects.filter(name="Admin Venue").exists()


@pytest.mark.django_db
class TestVenueDetailView:
    """Tests for venue detail endpoint."""
    
    def get_url(self, venue_id):
        return f"/api/venues/{venue_id}/"
    
    def test_get_venue_detail(self, api_client, venue):
        """Test getting venue details."""
        response = api_client.get(self.get_url(venue.id))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == venue.id
        assert response.data["name"] == venue.name
        assert response.data["address"] == venue.address
        assert response.data["description"] == venue.description
        assert "amenities" in response.data
        assert "images" in response.data
    
    def test_venue_not_found(self, api_client):
        """Test getting non-existent venue."""
        response = api_client.get(self.get_url(99999))
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_venue_requires_admin(self, authenticated_client, venue):
        """Test that updating venue requires admin."""
        response = authenticated_client.patch(self.get_url(venue.id), {
            "name": "Updated Name",
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_venue_as_admin(self, admin_client, venue):
        """Test that admin can update venue."""
        response = admin_client.patch(self.get_url(venue.id), {
            "name": "Updated by Admin",
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        venue.refresh_from_db()
        assert venue.name == "Updated by Admin"
    
    def test_delete_venue_soft_deletes(self, admin_client, venue):
        """Test that deleting a venue soft-deletes it."""
        response = admin_client.delete(self.get_url(venue.id))
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Venue should be inactive, not deleted
        venue.refresh_from_db()
        assert venue.is_active is False


@pytest.mark.django_db
class TestVenueAvailabilityView:
    """Tests for venue availability endpoint."""
    
    def get_url(self, venue_id):
        return f"/api/venues/{venue_id}/availability/"
    
    def test_get_availability_requires_date(self, api_client, venue):
        """Test that date parameter is required."""
        response = api_client.get(self.get_url(venue.id))
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_availability_success(self, api_client, venue):
        """Test getting availability for a date."""
        tomorrow = date.today() + timedelta(days=1)
        response = api_client.get(self.get_url(venue.id), {
            "date": tomorrow.isoformat(),
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["venue_id"] == venue.id
        # Date may be returned as date object or string
        response_date = response.data["date"]
        if hasattr(response_date, 'isoformat'):
            assert response_date == tomorrow
        else:
            assert response_date == tomorrow.isoformat()
        assert "time_slots" in response.data
        
        # Should have slots from 9 AM to 10 PM (13 hourly slots)
        assert len(response.data["time_slots"]) == 13
    
    def test_availability_shows_booked_slots(self, api_client, venue, user, db):
        """Test that booked slots are marked as unavailable."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create a booking for 10-12
        Booking.objects.create(
            user=user,
            venue=venue,
            booking_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status=BookingStatus.CONFIRMED,
        )
        
        response = api_client.get(self.get_url(venue.id), {
            "date": tomorrow.isoformat(),
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Find the 10-11 and 11-12 slots
        # Times may be returned as time objects or strings
        slots = {}
        for s in response.data["time_slots"]:
            start = s["start_time"]
            end = s["end_time"]
            # Convert to string for comparison if needed
            start_str = start.strftime("%H:%M:%S") if hasattr(start, 'strftime') else start
            end_str = end.strftime("%H:%M:%S") if hasattr(end, 'strftime') else end
            slots[(start_str, end_str)] = s["is_available"]
        
        # 10:00-11:00 and 11:00-12:00 should be unavailable
        assert slots.get(("10:00:00", "11:00:00")) is False
        assert slots.get(("11:00:00", "12:00:00")) is False
        
        # 09:00-10:00 and 12:00-13:00 should be available
        assert slots.get(("09:00:00", "10:00:00")) is True
        assert slots.get(("12:00:00", "13:00:00")) is True
    
    def test_venue_not_found(self, api_client):
        """Test availability for non-existent venue."""
        tomorrow = date.today() + timedelta(days=1)
        response = api_client.get(self.get_url(99999), {
            "date": tomorrow.isoformat(),
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestVenueTranslations:
    """Tests for venue translations via Accept-Language header."""
    
    url = "/api/venues/"
    
    def test_default_language_russian(self, api_client, venue):
        """Test that default language is Russian."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        # Without Accept-Language, should return Russian (default)
        result = response.data["results"][0]
        assert result["name"] == venue.name_ru or result["name"] == venue.name
    
    def test_uzbek_language(self, api_client, venue):
        """Test getting venue in Uzbek."""
        response = api_client.get(
            self.url,
            HTTP_ACCEPT_LANGUAGE="uz"
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_english_language(self, api_client, venue):
        """Test getting venue in English."""
        response = api_client.get(
            self.url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        
        assert response.status_code == status.HTTP_200_OK
