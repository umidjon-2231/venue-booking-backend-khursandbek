"""
Admin configuration for users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Enhanced admin configuration for custom User model.
    """
    
    list_display = (
        "phone_number",
        "name",
        "is_active",
        "verification_badge",
        "is_staff",
        "booking_count",
        "created_at",
    )
    list_filter = ("is_active", "is_verified", "is_staff", "is_superuser", "created_at")
    search_fields = ("phone_number", "name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_login", "booking_stats")
    list_per_page = 25
    date_hierarchy = "created_at"
    
    fieldsets = (
        (None, {"fields": ("phone_number",)}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Statistics"), {
            "fields": ("booking_stats",),
            "classes": ("collapse",),
        }),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "name", "is_verified", "is_staff"),
            },
        ),
    )
    
    actions = ["verify_users", "unverify_users", "activate_users", "deactivate_users"]
    
    def get_queryset(self, request):
        """Annotate queryset with booking count."""
        return super().get_queryset(request).annotate(
            _booking_count=Count("bookings")
        )
    
    def verification_badge(self, obj):
        """Display verification status with colored badge."""
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 2px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #d9534f; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">✗ Unverified</span>'
        )
    verification_badge.short_description = _("status")
    
    def booking_count(self, obj):
        """Display booking count with link to bookings."""
        count = getattr(obj, "_booking_count", 0)
        if count > 0:
            return format_html(
                '<a href="/admin/bookings/booking/?user__id__exact={}">{} booking(s)</a>',
                obj.id,
                count,
            )
        return "0"
    booking_count.short_description = _("bookings")
    booking_count.admin_order_field = "_booking_count"
    
    def booking_stats(self, obj):
        """Display detailed booking statistics."""
        from apps.bookings.models import Booking, BookingStatus
        
        bookings = Booking.objects.filter(user=obj)
        total = bookings.count()
        pending = bookings.filter(status=BookingStatus.PENDING).count()
        confirmed = bookings.filter(status=BookingStatus.CONFIRMED).count()
        completed = bookings.filter(status=BookingStatus.COMPLETED).count()
        cancelled = bookings.filter(status=BookingStatus.CANCELLED).count()
        
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>Total:</strong> {} | '
            '<span style="color: #f0ad4e;">Pending: {}</span> | '
            '<span style="color: #5cb85c;">Confirmed: {}</span> | '
            '<span style="color: #5bc0de;">Completed: {}</span> | '
            '<span style="color: #d9534f;">Cancelled: {}</span>'
            '</div>',
            total, pending, confirmed, completed, cancelled,
        )
    booking_stats.short_description = _("booking statistics")
    
    @admin.action(description=_("Verify selected users"))
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} user(s) verified.")
    
    @admin.action(description=_("Unverify selected users"))
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} user(s) unverified.")
    
    @admin.action(description=_("Activate selected users"))
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated.")
    
    @admin.action(description=_("Deactivate selected users"))
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")
