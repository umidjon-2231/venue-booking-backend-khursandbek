"""
Services for venues app.
"""

from datetime import date, datetime, time, timedelta
from typing import List, Dict, Any

from django.conf import settings


def get_available_time_slots(venue_id: int, check_date: date) -> List[Dict[str, Any]]:
    """
    Get available time slots for a venue on a specific date.
    
    Args:
        venue_id: ID of the venue to check
        check_date: Date to check availability for
        
    Returns:
        List of time slots with availability status
    """
    from apps.bookings.models import Booking
    
    start_hour = getattr(settings, "BOOKING_START_HOUR", 9)
    end_hour = getattr(settings, "BOOKING_END_HOUR", 22)
    
    # Get all confirmed/pending bookings for this venue on this date
    existing_bookings = Booking.objects.filter(
        venue_id=venue_id,
        booking_date=check_date,
        status__in=["pending", "confirmed"],
    ).values_list("start_time", "end_time")
    
    # Convert to list of tuples for easier checking
    booked_slots = [(b[0], b[1]) for b in existing_bookings]
    
    # Generate hourly time slots
    time_slots = []
    for hour in range(start_hour, end_hour):
        slot_start = time(hour=hour)
        slot_end = time(hour=hour + 1)
        
        # Check if this slot overlaps with any booking
        is_available = True
        for booked_start, booked_end in booked_slots:
            # Check for overlap
            if not (slot_end <= booked_start or slot_start >= booked_end):
                is_available = False
                break
        
        time_slots.append({
            "start_time": slot_start,
            "end_time": slot_end,
            "is_available": is_available,
        })
    
    return time_slots
