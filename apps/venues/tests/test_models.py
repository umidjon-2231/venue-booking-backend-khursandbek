"""
Tests for Venue model.
"""

from decimal import Decimal

import pytest

from apps.venues.models import Venue


@pytest.mark.django_db
class TestVenueModel:
    """Tests for the Venue model."""
    
    def test_create_venue(self):
        """Test creating a venue."""
        venue = Venue.objects.create(
            name="Test Venue",
            address="123 Test Street",
            description="A test venue",
            price_per_hour=Decimal("100000.00"),
        )
        
        assert venue.name == "Test Venue"
        assert venue.address == "123 Test Street"
        assert venue.price_per_hour == Decimal("100000.00")
        assert venue.is_active is True
        assert venue.images == []
        assert venue.amenities == []
    
    def test_venue_with_images(self):
        """Test venue with image URLs."""
        images = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
        ]
        venue = Venue.objects.create(
            name="Venue with Images",
            address="456 Image Street",
            price_per_hour=Decimal("150000.00"),
            images=images,
        )
        
        assert venue.images == images
        assert venue.image_count == 2
    
    def test_venue_with_amenities(self):
        """Test venue with amenities."""
        amenities = ["WiFi", "Parking", "AC"]
        venue = Venue.objects.create(
            name="Venue with Amenities",
            address="789 Amenity Ave",
            price_per_hour=Decimal("200000.00"),
            amenities=amenities,
        )
        
        assert venue.amenities == amenities
    
    def test_str_representation(self, venue):
        """Test string representation."""
        assert str(venue) == venue.name
    
    def test_active_manager_excludes_inactive(self, venue, inactive_venue):
        """Test that default manager excludes inactive venues."""
        venues = Venue.objects.all()
        
        assert venue in venues
        assert inactive_venue not in venues
    
    def test_all_objects_manager_includes_inactive(self, venue, inactive_venue):
        """Test that all_objects manager includes inactive venues."""
        venues = Venue.all_objects.all()
        
        assert venue in venues
        assert inactive_venue in venues
    
    def test_deactivate_venue(self, venue):
        """Test deactivating a venue."""
        assert venue.is_active is True
        
        venue.deactivate()
        
        venue.refresh_from_db()
        assert venue.is_active is False
    
    def test_activate_venue(self, inactive_venue):
        """Test activating a venue."""
        assert inactive_venue.is_active is False
        
        inactive_venue.activate()
        
        inactive_venue.refresh_from_db()
        assert inactive_venue.is_active is True
    
    def test_venue_ordering(self, db):
        """Test venues are ordered by created_at descending."""
        from time import sleep
        
        venue1 = Venue.objects.create(
            name="First",
            address="First address",
            price_per_hour=Decimal("100000.00"),
        )
        sleep(0.01)  # Small delay to ensure different timestamps
        venue2 = Venue.objects.create(
            name="Second",
            address="Second address",
            price_per_hour=Decimal("100000.00"),
        )
        
        venues = list(Venue.objects.all())
        
        # Most recent first
        assert venues[0] == venue2
        assert venues[1] == venue1
