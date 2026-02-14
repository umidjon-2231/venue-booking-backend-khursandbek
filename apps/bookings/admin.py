"""
Admin configuration for bookings app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Booking, BookingStatus


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for Booking model with enhanced features.
    """
    
    list_display = (
        "id",
        "user_display",
        "venue_display",
        "booking_date",
        "time_range",
        "total_price_display",
        "status_badge",
        "created_at",
    )
    list_filter = ("status", "booking_date", "created_at", "venue")
    search_fields = (
        "user__phone_number",
        "user__name",
        "venue__name",
        "venue__name_ru",
        "venue__name_uz",
        "venue__name_en",
    )
    readonly_fields = ("total_price", "created_at", "updated_at", "duration_display")
    ordering = ("-created_at",)
    date_hierarchy = "booking_date"
    list_per_page = 25
    list_select_related = ("user", "venue")
    
    # Enable inline status editing
    list_editable = ("status",) if False else ()  # Disabled for safety, enable if needed
    
    fieldsets = (
        (None, {
            "fields": ("user", "venue"),
        }),
        (_("Booking Details"), {
            "fields": ("booking_date", "start_time", "end_time", "duration_display", "total_price"),
        }),
        (_("Status"), {
            "fields": ("status",),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    actions = [
        "mark_confirmed",
        "mark_completed",
        "mark_cancelled",
        "mark_pending",
        "export_as_csv",
    ]
    
    def user_display(self, obj):
        """Display user with phone number."""
        if obj.user.name:
            return f"{obj.user.name} ({obj.user.phone_number})"
        return obj.user.phone_number
    user_display.short_description = _("user")
    user_display.admin_order_field = "user__phone_number"
    
    def venue_display(self, obj):
        """Display venue name."""
        return obj.venue.name
    venue_display.short_description = _("venue")
    venue_display.admin_order_field = "venue__name"
    
    def time_range(self, obj):
        """Display formatted time range."""
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_range.short_description = _("time")
    
    def duration_display(self, obj):
        """Display booking duration."""
        from datetime import datetime, timedelta
        start = datetime.combine(obj.booking_date, obj.start_time)
        end = datetime.combine(obj.booking_date, obj.end_time)
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if minutes:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    duration_display.short_description = _("duration")
    
    def total_price_display(self, obj):
        """Display formatted price."""
        return f"{obj.total_price:,.0f} UZS"
    total_price_display.short_description = _("price")
    total_price_display.admin_order_field = "total_price"
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            BookingStatus.PENDING: "#f0ad4e",      # Orange
            BookingStatus.CONFIRMED: "#5cb85c",    # Green
            BookingStatus.CANCELLED: "#d9534f",    # Red
            BookingStatus.COMPLETED: "#5bc0de",    # Blue
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )
    status_badge.short_description = _("status")
    status_badge.admin_order_field = "status"
    
    @admin.action(description=_("Mark selected bookings as pending"))
    def mark_pending(self, request, queryset):
        updated = queryset.update(status=BookingStatus.PENDING)
        self.message_user(request, f"{updated} booking(s) marked as pending.")
    
    @admin.action(description=_("Mark selected bookings as confirmed"))
    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(
            status__in=[BookingStatus.PENDING]
        ).update(status=BookingStatus.CONFIRMED)
        self.message_user(request, f"{updated} booking(s) marked as confirmed.")
    
    @admin.action(description=_("Mark selected bookings as completed"))
    def mark_completed(self, request, queryset):
        updated = queryset.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).update(status=BookingStatus.COMPLETED)
        self.message_user(request, f"{updated} booking(s) marked as completed.")
    
    @admin.action(description=_("Mark selected bookings as cancelled"))
    def mark_cancelled(self, request, queryset):
        updated = queryset.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).update(status=BookingStatus.CANCELLED)
        self.message_user(request, f"{updated} booking(s) marked as cancelled.")
    
    @admin.action(description=_("Export selected bookings as CSV"))
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=bookings_export.csv"
        
        writer = csv.writer(response)
        writer.writerow([
            "ID", "User Phone", "User Name", "Venue", "Date",
            "Start Time", "End Time", "Price", "Status", "Created At"
        ])
        
        for booking in queryset.select_related("user", "venue"):
            writer.writerow([
                booking.id,
                booking.user.phone_number,
                booking.user.name or "",
                booking.venue.name,
                booking.booking_date.isoformat(),
                booking.start_time.strftime("%H:%M"),
                booking.end_time.strftime("%H:%M"),
                str(booking.total_price),
                booking.get_status_display(),
                booking.created_at.isoformat(),
            ])
        
        return response
