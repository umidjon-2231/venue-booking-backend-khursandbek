"""
Tests for authentication views.
"""

from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSendOTPView:
    """Tests for send OTP endpoint."""
    
    url = "/api/auth/send-otp/"
    
    def test_send_otp_success(self, api_client):
        """Test sending OTP with valid phone number."""
        response = api_client.post(self.url, {
            "phone_number": "+998901234567"
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "OTP sent successfully"
        assert response.data["phone_number"] == "+998901234567"
    
    def test_send_otp_invalid_phone_format(self, api_client):
        """Test sending OTP with invalid phone format."""
        response = api_client.post(self.url, {
            "phone_number": "12345"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_details = response.data.get("error", {}).get("details", response.data)
        assert "phone_number" in error_details
    
    def test_send_otp_missing_phone(self, api_client):
        """Test sending OTP without phone number."""
        response = api_client.post(self.url, {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_send_otp_non_uzbek_phone(self, api_client):
        """Test sending OTP with non-Uzbekistan phone number."""
        response = api_client.post(self.url, {
            "phone_number": "+1234567890"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVerifyOTPView:
    """Tests for verify OTP endpoint."""
    
    send_url = "/api/auth/send-otp/"
    verify_url = "/api/auth/verify-otp/"
    
    def test_verify_otp_success(self, api_client):
        """Test verifying OTP successfully."""
        phone = "+998901234567"
        
        # Send OTP first
        api_client.post(self.send_url, {"phone_number": phone})
        
        # Get OTP from cache
        from django.core.cache import cache
        otp = cache.get(f"otp:{phone}")
        
        # Verify OTP
        response = api_client.post(self.verify_url, {
            "phone_number": phone,
            "otp": otp,
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
    
    def test_verify_otp_creates_user(self, api_client):
        """Test that verifying OTP creates new user if not exists."""
        from apps.users.models import User
        
        phone = "+998901111111"
        
        # Send and verify OTP
        api_client.post(self.send_url, {"phone_number": phone})
        
        from django.core.cache import cache
        otp = cache.get(f"otp:{phone}")
        
        response = api_client.post(self.verify_url, {
            "phone_number": phone,
            "otp": otp,
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert User.objects.filter(phone_number=phone).exists()
        
        user = User.objects.get(phone_number=phone)
        assert user.is_verified is True
    
    def test_verify_otp_invalid(self, api_client):
        """Test verifying with wrong OTP."""
        phone = "+998901234567"
        
        api_client.post(self.send_url, {"phone_number": phone})
        
        response = api_client.post(self.verify_url, {
            "phone_number": phone,
            "otp": "000000",
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_verify_otp_expired(self, api_client):
        """Test verifying when OTP doesn't exist."""
        response = api_client.post(self.verify_url, {
            "phone_number": "+998901234567",
            "otp": "123456",
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRefreshTokenView:
    """Tests for refresh token endpoint."""
    
    url = "/api/auth/refresh/"
    
    def test_refresh_token_success(self, api_client, user):
        """Test refreshing access token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        
        response = api_client.post(self.url, {
            "refresh": str(refresh),
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
    
    def test_refresh_token_invalid(self, api_client):
        """Test refreshing with invalid token."""
        response = api_client.post(self.url, {
            "refresh": "invalid-token",
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_missing(self, api_client):
        """Test refreshing without token."""
        response = api_client.post(self.url, {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfileView:
    """Tests for user profile endpoint."""
    
    url = "/api/auth/me/"
    
    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test getting profile when authenticated."""
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone_number"] == user.phone_number
        assert response.data["name"] == user.name
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        response = authenticated_client.patch(self.url, {
            "name": "Updated Name",
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.name == "Updated Name"
    
    def test_cannot_update_phone_number(self, authenticated_client, user):
        """Test that phone number cannot be updated via profile."""
        original_phone = user.phone_number
        
        response = authenticated_client.patch(self.url, {
            "phone_number": "+998909999999",
        })
        
        user.refresh_from_db()
        assert user.phone_number == original_phone
