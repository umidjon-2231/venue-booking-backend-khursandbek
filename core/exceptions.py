"""
Custom exceptions for the venue-booking-backend project.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class OTPException(APIException):
    """Base exception for OTP-related errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "OTP error occurred."
    default_code = "otp_error"


class OTPExpiredException(OTPException):
    """Exception raised when OTP has expired."""
    default_detail = "OTP has expired. Please request a new one."
    default_code = "otp_expired"


class OTPInvalidException(OTPException):
    """Exception raised when OTP is invalid."""
    default_detail = "Invalid OTP. Please try again."
    default_code = "otp_invalid"


class OTPRateLimitException(OTPException):
    """Exception raised when OTP rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Too many OTP requests. Please try again later."
    default_code = "otp_rate_limit"


class BookingException(APIException):
    """Base exception for booking-related errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Booking error occurred."
    default_code = "booking_error"


class VenueNotAvailableException(BookingException):
    """Exception raised when venue is not available for the requested time."""
    default_detail = "Venue is not available for the requested time slot."
    default_code = "venue_not_available"


class BookingTimeInvalidException(BookingException):
    """Exception raised when booking time is outside allowed hours."""
    default_detail = "Booking time is outside allowed hours (9 AM - 10 PM)."
    default_code = "booking_time_invalid"


class BookingCancellationException(BookingException):
    """Exception raised when booking cannot be cancelled."""
    default_detail = "This booking cannot be cancelled."
    default_code = "booking_cancellation_error"
