"""
OTP service for handling OTP generation, storage, and verification.
"""

import logging

from django.conf import settings
from django.core.cache import cache

from core.exceptions import OTPExpiredException, OTPInvalidException, OTPRateLimitException
from core.utils import generate_otp, get_otp_attempt_cache_key, get_otp_cache_key

logger = logging.getLogger(__name__)


class OTPService:
    """
    Service class for OTP operations.
    """
    
    @staticmethod
    def send_otp(phone_number: str) -> str:
        """
        Generate and send OTP to the given phone number.
        
        Args:
            phone_number: Phone number to send OTP to
            
        Returns:
            Generated OTP (for development/testing)
            
        Raises:
            OTPRateLimitException: If rate limit is exceeded
        """
        # Check rate limit
        attempt_key = get_otp_attempt_cache_key(phone_number)
        attempts = cache.get(attempt_key, 0)
        
        max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 3)
        rate_limit_minutes = getattr(settings, "OTP_RATE_LIMIT_MINUTES", 10)
        
        if attempts >= max_attempts:
            raise OTPRateLimitException(
                f"Too many OTP requests. Please try again after {rate_limit_minutes} minutes."
            )
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in cache
        otp_key = get_otp_cache_key(phone_number)
        expiry_seconds = getattr(settings, "OTP_EXPIRY_SECONDS", 300)
        cache.set(otp_key, otp, timeout=expiry_seconds)
        
        # Update attempt counter
        cache.set(attempt_key, attempts + 1, timeout=rate_limit_minutes * 60)
        
        # Log OTP to console (mock SMS)
        logger.info(f"[MOCK SMS] OTP for {phone_number}: {otp}")
        print(f"\n{'='*50}")
        print(f"[MOCK SMS] OTP for {phone_number}: {otp}")
        print(f"{'='*50}\n")
        
        return otp
    
    @staticmethod
    def verify_otp(phone_number: str, otp: str) -> bool:
        """
        Verify the OTP for the given phone number.
        
        Args:
            phone_number: Phone number to verify OTP for
            otp: OTP to verify
            
        Returns:
            True if OTP is valid
            
        Raises:
            OTPExpiredException: If OTP has expired or doesn't exist
            OTPInvalidException: If OTP is invalid
        """
        otp_key = get_otp_cache_key(phone_number)
        stored_otp = cache.get(otp_key)
        
        if stored_otp is None:
            raise OTPExpiredException()
        
        if stored_otp != otp:
            raise OTPInvalidException()
        
        # Delete OTP after successful verification
        cache.delete(otp_key)
        
        # Clear attempt counter
        attempt_key = get_otp_attempt_cache_key(phone_number)
        cache.delete(attempt_key)
        
        return True
