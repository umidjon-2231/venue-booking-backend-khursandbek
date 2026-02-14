"""
Admin configuration for venues app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Venue, VenueImage


class VenueImageInline(admin.TabularInline):
    """
    Inline admin for venue images with drag-and-drop ordering.
    """
    
    model = VenueImage
    extra = 1
    fields = ("image", "image_preview", "alt_text", "is_primary", "order")
    readonly_fields = ("image_preview",)
    ordering = ("order", "-created_at")
    
    def image_preview(self, obj):
        """Display thumbnail preview of the image."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 75px;" />',
                obj.image.url,
            )
        return _("No image")
    image_preview.short_description = _("preview")


@admin.register(Venue)
class VenueAdmin(TabbedTranslationAdmin):
    """
    Admin configuration for Venue model with tabbed translation support.
    Uses TabbedTranslationAdmin for better multi-language editing experience.
    """
    
    list_display = (
        "name",
        "address_short",
        "price_per_hour",
        "is_active",
        "image_count_display",
        "primary_image_preview",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "price_per_hour")
    search_fields = (
        "name", "name_ru", "name_uz", "name_en",
        "address", "address_ru", "address_uz", "address_en",
        "description",
    )
    readonly_fields = ("created_at", "updated_at", "images_preview", "all_images_preview")
    ordering = ("-created_at",)
    list_editable = ("is_active", "price_per_hour")
    list_per_page = 20
    
    # Inline for uploaded images
    inlines = [VenueImageInline]
    
    fieldsets = (
        (None, {
            "fields": ("name", "address", "description"),
            "description": _("Use tabs above to edit translations for each language."),
        }),
        (_("Pricing"), {
            "fields": ("price_per_hour",),
        }),
        (_("External Image URLs"), {
            "fields": ("images", "images_preview"),
            "classes": ("collapse",),
            "description": _("Legacy URL-based images. Use 'Venue Images' section below for file uploads."),
        }),
        (_("Amenities"), {
            "fields": ("amenities",),
        }),
        (_("Status"), {
            "fields": ("is_active",),
        }),
        (_("All Images Preview"), {
            "fields": ("all_images_preview",),
            "classes": ("collapse",),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    # Custom admin actions
    actions = ["activate_venues", "deactivate_venues", "duplicate_venue"]
    
    def address_short(self, obj):
        """Display truncated address."""
        if obj.address and len(obj.address) > 50:
            return obj.address[:50] + "..."
        return obj.address or ""
    address_short.short_description = _("address")
    
    def image_count_display(self, obj):
        """Display image count."""
        return obj.image_count
    image_count_display.short_description = _("images")
    
    def primary_image_preview(self, obj):
        """Display primary image thumbnail in list view."""
        primary = obj.primary_image
        if primary:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 40px; border-radius: 4px;" />',
                primary,
            )
        return format_html('<span style="color: #999;">—</span>')
    primary_image_preview.short_description = _("thumbnail")
    
    def images_preview(self, obj):
        """Display URL-based image previews in admin."""
        if not obj.images:
            return _("No external images")
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for url in obj.images[:5]:
            html += f'<img src="{url}" style="max-width: 150px; max-height: 100px; border-radius: 4px;" />'
        
        if len(obj.images) > 5:
            html += f"<p style='margin: auto 0;'>... and {len(obj.images) - 5} more</p>"
        
        html += '</div>'
        return format_html(html)
    images_preview.short_description = _("external images preview")
    
    def all_images_preview(self, obj):
        """Display all images (uploaded + URL-based) in admin."""
        all_urls = obj.all_image_urls if hasattr(obj, 'all_image_urls') else []
        if not all_urls:
            return _("No images")
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for url in all_urls[:10]:
            html += f'<img src="{url}" style="max-width: 150px; max-height: 100px; border-radius: 4px;" />'
        
        if len(all_urls) > 10:
            html += f"<p style='margin: auto 0;'>... and {len(all_urls) - 10} more</p>"
        
        html += '</div>'
        return format_html(html)
    all_images_preview.short_description = _("all images preview")
    
    def get_queryset(self, request):
        """Use all_objects manager to show inactive venues too."""
        return Venue.all_objects.prefetch_related("uploaded_images").all()
    
    @admin.action(description=_("Activate selected venues"))
    def activate_venues(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} venue(s) activated.")
    
    @admin.action(description=_("Deactivate selected venues"))
    def deactivate_venues(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} venue(s) deactivated.")
    
    @admin.action(description=_("Duplicate selected venues"))
    def duplicate_venue(self, request, queryset):
        for venue in queryset:
            # Create a copy with modified name
            venue.pk = None
            venue.name = f"{venue.name} (Copy)"
            venue.name_ru = f"{venue.name_ru} (Копия)" if venue.name_ru else None
            venue.name_uz = f"{venue.name_uz} (Nusxa)" if venue.name_uz else None
            venue.name_en = f"{venue.name_en} (Copy)" if venue.name_en else None
            venue.save()
        self.message_user(request, f"{queryset.count()} venue(s) duplicated.")


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    """
    Standalone admin for VenueImage model.
    """
    
    list_display = ("id", "venue", "image_preview", "alt_text", "is_primary", "order", "created_at")
    list_filter = ("is_primary", "venue", "created_at")
    search_fields = ("venue__name", "alt_text")
    list_editable = ("is_primary", "order")
    ordering = ("venue", "order", "-created_at")
    readonly_fields = ("created_at", "updated_at", "image_preview_large")
    
    fieldsets = (
        (None, {
            "fields": ("venue", "image", "image_preview_large"),
        }),
        (_("Details"), {
            "fields": ("alt_text", "is_primary", "order"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    def image_preview(self, obj):
        """Display thumbnail in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 60px; border-radius: 4px;" />',
                obj.image.url,
            )
        return _("No image")
    image_preview.short_description = _("preview")
    
    def image_preview_large(self, obj):
        """Display larger preview in detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px;" />',
                obj.image.url,
            )
        return _("No image")
    image_preview_large.short_description = _("image preview")
