"""
Booking models for the venue-booking-backend project.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class BookingStatus(models.TextChoices):
    """Booking status choices."""
    PENDING = "pending", _("Pending")
    CONFIRMED = "confirmed", _("Confirmed")
    CANCELLED = "cancelled", _("Cancelled")
    COMPLETED = "completed", _("Completed")


class Booking(TimeStampedModel):
    """
    Booking model representing a venue reservation.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("user"),
        db_index=True,  # Index for filtering by user
    )
    venue = models.ForeignKey(
        "venues.Venue",
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("venue"),
        db_index=True,  # Index for filtering by venue
    )
    booking_date = models.DateField(_("booking date"), db_index=True)  # Index for date queries
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    total_price = models.DecimalField(
        _("total price"),
        max_digits=10,
        decimal_places=2,
        editable=False,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        db_index=True,  # Index for status filtering
    )
    
    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        ordering = ["-booking_date", "-start_time"]
        # Composite index for double-booking prevention queries
        indexes = [
            models.Index(
                fields=["venue", "booking_date", "status"],
                name="booking_venue_date_status_idx",
            ),
            models.Index(
                fields=["user", "booking_date"],
                name="booking_user_date_idx",
            ),
        ]
        # Prevent double booking at database level
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="end_time_after_start_time",
            ),
        ]
    
    def __str__(self):
        return f"{self.venue.name} - {self.booking_date} ({self.start_time}-{self.end_time})"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        if not self.total_price:
            self.total_price = self.calculate_price()
        super().save(*args, **kwargs)
    
    def calculate_price(self) -> Decimal:
        """
        Calculate total price based on duration and venue's hourly rate.
        """
        from datetime import datetime, timedelta
        
        # Create datetime objects for calculation
        today = datetime.today().date()
        start_dt = datetime.combine(today, self.start_time)
        end_dt = datetime.combine(today, self.end_time)
        
        # Handle edge case where end_time might be on next day
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        # Calculate duration in hours
        duration_hours = Decimal((end_dt - start_dt).total_seconds()) / Decimal(3600)
        
        return round(self.venue.price_per_hour * duration_hours, 2)
    
    @property
    def duration_hours(self) -> float:
        """Get booking duration in hours."""
        from datetime import datetime, timedelta
        
        today = datetime.today().date()
        start_dt = datetime.combine(today, self.start_time)
        end_dt = datetime.combine(today, self.end_time)
        
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        return (end_dt - start_dt).total_seconds() / 3600
    
    @property
    def can_cancel(self) -> bool:
        """Check if booking can be cancelled."""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
    
    def cancel(self):
        """Cancel the booking."""
        if self.can_cancel:
            self.status = BookingStatus.CANCELLED
            self.save(update_fields=["status", "updated_at"])
            return True
        return False
