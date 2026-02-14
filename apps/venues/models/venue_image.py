"""
VenueImage model for handling venue image uploads.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


def venue_image_upload_path(instance, filename):
    """Generate upload path for venue images."""
    return f"venues/{instance.venue_id}/{filename}"


class VenueImage(TimeStampedModel):
    """
    Model for storing venue images with file upload support.
    """
    
    venue = models.ForeignKey(
        "venues.Venue",
        on_delete=models.CASCADE,
        related_name="uploaded_images",
        verbose_name=_("venue"),
    )
    image = models.ImageField(
        _("image"),
        upload_to=venue_image_upload_path,
    )
    alt_text = models.CharField(
        _("alt text"),
        max_length=255,
        blank=True,
        help_text=_("Alternative text for accessibility"),
    )
    is_primary = models.BooleanField(
        _("primary image"),
        default=False,
        help_text=_("Primary image shown in listings"),
    )
    order = models.PositiveIntegerField(
        _("order"),
        default=0,
        help_text=_("Display order (lower numbers first)"),
    )
    
    class Meta:
        verbose_name = _("venue image")
        verbose_name_plural = _("venue images")
        ordering = ["order", "-created_at"]
    
    def __str__(self):
        return f"{self.venue.name} - Image {self.pk}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per venue."""
        if self.is_primary:
            # Set all other images for this venue as non-primary
            VenueImage.objects.filter(
                venue=self.venue,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
