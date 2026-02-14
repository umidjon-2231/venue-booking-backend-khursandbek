"""
Pytest configuration and fixtures for venue-booking-backend.
"""

from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking, BookingStatus
from apps.users.models import User
from apps.venues.models import Venue


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a regular test user."""
    return User.objects.create_user(
        phone_number="+998901234567",
        name="Test User",
        is_verified=True,
    )


@pytest.fixture
def user2(db):
    """Create a second test user."""
    return User.objects.create_user(
        phone_number="+998901234568",
        name="Test User 2",
        is_verified=True,
    )


@pytest.fixture
def admin_user(db):
    """Create an admin/staff user."""
    return User.objects.create_superuser(
        phone_number="+998909999999",
        name="Admin User",
        password="adminpass123",
    )


@pytest.fixture
def unverified_user(db):
    """Create an unverified user."""
    return User.objects.create_user(
        phone_number="+998901111111",
        name="Unverified User",
        is_verified=False,
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an API client authenticated as the test user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an API client authenticated as admin."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def venue(db):
    """Create a test venue."""
    return Venue.objects.create(
        name="Test Venue",
        name_ru="Тестовая Площадка",
        name_uz="Test Maydoni",
        name_en="Test Venue",
        address="123 Test Street",
        address_ru="ул. Тестовая, 123",
        address_uz="Test ko'chasi, 123",
        address_en="123 Test Street",
        description="A great venue for testing",
        description_ru="Отличная площадка для тестирования",
        description_uz="Test uchun ajoyib maydon",
        description_en="A great venue for testing",
        price_per_hour=Decimal("100000.00"),
        images=[
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
        ],
        amenities=["WiFi", "Parking", "AC"],
        is_active=True,
    )


@pytest.fixture
def venue2(db):
    """Create a second test venue."""
    return Venue.objects.create(
        name="Second Venue",
        name_ru="Вторая Площадка",
        name_uz="Ikkinchi Maydon",
        name_en="Second Venue",
        address="456 Another Street",
        address_ru="ул. Другая, 456",
        address_uz="Boshqa ko'cha, 456",
        address_en="456 Another Street",
        description="Another venue for testing",
        price_per_hour=Decimal("200000.00"),
        images=["https://example.com/image3.jpg"],
        amenities=["WiFi", "Sound System"],
        is_active=True,
    )


@pytest.fixture
def inactive_venue(db):
    """Create an inactive venue."""
    return Venue.objects.create(
        name="Inactive Venue",
        address="789 Closed Street",
        description="This venue is inactive",
        price_per_hour=Decimal("50000.00"),
        is_active=False,
    )


@pytest.fixture
def booking(db, user, venue):
    """Create a test booking."""
    return Booking.objects.create(
        user=user,
        venue=venue,
        booking_date=date.today() + timedelta(days=1),
        start_time=time(10, 0),
        end_time=time(12, 0),
        status=BookingStatus.PENDING,
    )


@pytest.fixture
def confirmed_booking(db, user, venue):
    """Create a confirmed booking."""
    return Booking.objects.create(
        user=user,
        venue=venue,
        booking_date=date.today() + timedelta(days=2),
        start_time=time(14, 0),
        end_time=time(16, 0),
        status=BookingStatus.CONFIRMED,
    )


@pytest.fixture
def cancelled_booking(db, user, venue):
    """Create a cancelled booking."""
    return Booking.objects.create(
        user=user,
        venue=venue,
        booking_date=date.today() + timedelta(days=3),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status=BookingStatus.CANCELLED,
    )


@pytest.fixture
def completed_booking(db, user, venue):
    """Create a completed booking."""
    return Booking.objects.create(
        user=user,
        venue=venue,
        booking_date=date.today() - timedelta(days=1),
        start_time=time(10, 0),
        end_time=time(12, 0),
        status=BookingStatus.COMPLETED,
    )


@pytest.fixture
def mock_cache():
    """Mock the Django cache for OTP tests."""
    with patch("django.core.cache.cache") as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        yield mock
