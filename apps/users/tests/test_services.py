"""
Tests for OTP service.
"""

from unittest.mock import patch

import pytest
from django.core.cache import cache

from apps.users.services import OTPService
from core.exceptions import OTPExpiredException, OTPInvalidException, OTPRateLimitException


@pytest.mark.django_db
class TestOTPService:
    """Tests for OTP service."""
    
    def test_send_otp_generates_6_digit_code(self):
        """Test that OTP is 6 digits."""
        phone = "+998901234567"
        otp = OTPService.send_otp(phone)
        
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_send_otp_stores_in_cache(self):
        """Test that OTP is stored in cache."""
        phone = "+998901234567"
        otp = OTPService.send_otp(phone)
        
        cached_otp = cache.get(f"otp:{phone}")
        assert cached_otp == otp
    
    def test_send_otp_rate_limit(self):
        """Test rate limiting on OTP requests."""
        phone = "+998901234567"
        
        # Send 3 OTPs (max allowed)
        OTPService.send_otp(phone)
        OTPService.send_otp(phone)
        OTPService.send_otp(phone)
        
        # 4th request should be rate limited
        with pytest.raises(OTPRateLimitException):
            OTPService.send_otp(phone)
    
    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        phone = "+998901234567"
        otp = OTPService.send_otp(phone)
        
        result = OTPService.verify_otp(phone, otp)
        assert result is True
    
    def test_verify_otp_clears_cache(self):
        """Test that OTP is deleted after successful verification."""
        phone = "+998901234567"
        otp = OTPService.send_otp(phone)
        
        OTPService.verify_otp(phone, otp)
        
        # OTP should be cleared
        assert cache.get(f"otp:{phone}") is None
    
    def test_verify_otp_invalid(self):
        """Test verification with wrong OTP."""
        phone = "+998901234567"
        OTPService.send_otp(phone)
        
        with pytest.raises(OTPInvalidException):
            OTPService.verify_otp(phone, "000000")
    
    def test_verify_otp_expired(self):
        """Test verification when OTP doesn't exist (expired)."""
        phone = "+998901234567"
        
        with pytest.raises(OTPExpiredException):
            OTPService.verify_otp(phone, "123456")
    
    def test_verify_otp_clears_attempt_counter(self):
        """Test that attempt counter is cleared after successful verification."""
        phone = "+998901234567"
        
        # Use 2 attempts
        OTPService.send_otp(phone)
        otp = OTPService.send_otp(phone)
        
        # Verify successfully
        OTPService.verify_otp(phone, otp)
        
        # Should be able to send 3 more OTPs
        OTPService.send_otp(phone)
        OTPService.send_otp(phone)
        OTPService.send_otp(phone)
        
        # 4th should fail
        with pytest.raises(OTPRateLimitException):
            OTPService.send_otp(phone)
