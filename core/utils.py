"""
Utility functions for the venue-booking-backend project.
"""

import random
import re
import string

from django.conf import settings


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP of the specified length.
    
    Args:
        length: Length of the OTP (default: 6)
        
    Returns:
        A string containing the numeric OTP
    """
    return "".join(random.choices(string.digits, k=length))


def validate_uzbekistan_phone(phone: str) -> bool:
    """
    Validate Uzbekistan phone number format.
    Expected format: +998XXXXXXXXX (12 digits total including +998)
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r"^\+998[0-9]{9}$"
    return bool(re.match(pattern, phone))


def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard format.
    Removes spaces, dashes, and ensures proper +998 prefix.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)
    
    # Ensure it starts with +998
    if cleaned.startswith("998") and not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    elif cleaned.startswith("8") and len(cleaned) == 10:
        cleaned = "+998" + cleaned[1:]
    
    return cleaned


def get_otp_cache_key(phone: str) -> str:
    """
    Generate cache key for OTP storage.
    
    Args:
        phone: Phone number
        
    Returns:
        Cache key string
    """
    return f"otp:{phone}"


def get_otp_attempt_cache_key(phone: str) -> str:
    """
    Generate cache key for OTP attempt tracking.
    
    Args:
        phone: Phone number
        
    Returns:
        Cache key string
    """
    return f"otp_attempts:{phone}"


def calculate_booking_price(price_per_hour: float, start_time, end_time) -> float:
    """
    Calculate total booking price based on duration.
    
    Args:
        price_per_hour: Venue's hourly rate
        start_time: Booking start time
        end_time: Booking end time
        
    Returns:
        Total price as float
    """
    from datetime import datetime, timedelta
    
    # Calculate duration in hours
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M").time()
    
    # Create datetime objects for calculation
    today = datetime.today().date()
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)
    
    # Handle overnight bookings if needed
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    
    duration_hours = (end_dt - start_dt).total_seconds() / 3600
    
    return round(price_per_hour * duration_hours, 2)


def is_valid_booking_time(start_time, end_time) -> bool:
    """
    Check if booking time is within allowed hours.
    
    Args:
        start_time: Booking start time
        end_time: Booking end time
        
    Returns:
        True if valid, False otherwise
    """
    from datetime import time
    
    start_hour = getattr(settings, "BOOKING_START_HOUR", 9)
    end_hour = getattr(settings, "BOOKING_END_HOUR", 22)
    
    min_time = time(hour=start_hour)
    max_time = time(hour=end_hour)
    
    if isinstance(start_time, str):
        from datetime import datetime
        start_time = datetime.strptime(start_time, "%H:%M").time()
    if isinstance(end_time, str):
        from datetime import datetime
        end_time = datetime.strptime(end_time, "%H:%M").time()
    
    return min_time <= start_time and end_time <= max_time
