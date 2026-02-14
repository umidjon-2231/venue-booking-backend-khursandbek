"""
Model translation configuration for venues app.
"""

from modeltranslation.translator import TranslationOptions, register

from .models import Venue


@register(Venue)
class VenueTranslationOptions(TranslationOptions):
    """
    Translation options for Venue model.
    Enables translations for name, address, description, and amenities.
    """
    
    fields = ("name", "address", "description")
    # Note: amenities is an ArrayField and requires special handling
    # We'll handle amenities translations through a separate approach if needed
