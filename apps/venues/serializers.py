"""
Serializers for venues app.
"""

from rest_framework import serializers

from .models import Venue, VenueImage


class VenueImageSerializer(serializers.ModelSerializer):
    """
    Serializer for venue images.
    """
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VenueImage
        fields = ("id", "image", "image_url", "alt_text", "is_primary", "order")
        read_only_fields = ("id",)
    
    def get_image_url(self, obj):
        """Return absolute URL for the image."""
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class VenueListSerializer(serializers.ModelSerializer):
    """
    Serializer for venue list view.
    Returns minimal venue information for listing.
    """
    
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = (
            "id",
            "name",
            "address",
            "price_per_hour",
            "primary_image",
            "images",
            "is_active",
        )
    
    def get_primary_image(self, obj):
        """Return the primary image URL."""
        return obj.primary_image


class VenueDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for venue detail view.
    Returns full venue information.
    """
    
    uploaded_images = VenueImageSerializer(many=True, read_only=True)
    all_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = (
            "id",
            "name",
            "address",
            "description",
            "price_per_hour",
            "images",
            "uploaded_images",
            "all_images",
            "amenities",
            "is_active",
            "created_at",
            "updated_at",
        )
    
    def get_all_images(self, obj):
        """Return all image URLs (uploaded + external)."""
        return obj.all_image_urls


class VenueCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating venues (admin only).
    """
    
    class Meta:
        model = Venue
        fields = (
            "name",
            "address",
            "description",
            "price_per_hour",
            "images",
            "amenities",
            "is_active",
        )
    
    def validate_price_per_hour(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate_images(self, value):
        """Validate image URLs."""
        if value:
            for url in value:
                if not url.startswith(("http://", "https://")):
                    raise serializers.ValidationError(
                        f"Invalid image URL: {url}. Must start with http:// or https://"
                    )
        return value


class TimeSlotSerializer(serializers.Serializer):
    """
    Serializer for available time slots.
    """
    
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    is_available = serializers.BooleanField()


class AvailabilityRequestSerializer(serializers.Serializer):
    """
    Serializer for availability check request.
    """
    
    date = serializers.DateField(required=True)


class VenueAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for venue availability response.
    """
    
    venue_id = serializers.IntegerField()
    date = serializers.DateField()
    time_slots = TimeSlotSerializer(many=True)
