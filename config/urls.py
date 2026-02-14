"""
URL configuration for venue-booking-backend project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """API Root - lists all available endpoints."""
    return Response({
        "auth": {
            "send_otp": reverse("send-otp", request=request, format=format),
            "verify_otp": reverse("verify-otp", request=request, format=format),
            "token_refresh": reverse("token-refresh", request=request, format=format),
            "me": reverse("user-profile", request=request, format=format),
        },
        "venues": reverse("venue-list", request=request, format=format),
        "bookings": reverse("booking-list-create", request=request, format=format),
        "documentation": {
            "swagger": reverse("swagger-ui", request=request, format=format),
            "redoc": reverse("redoc", request=request, format=format),
            "schema": reverse("schema", request=request, format=format),
        },
    })


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # API Root
    path("api/", api_root, name="api-root"),
    
    # API endpoints
    path("api/auth/", include("apps.users.urls")),
    path("api/venues/", include("apps.venues.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
