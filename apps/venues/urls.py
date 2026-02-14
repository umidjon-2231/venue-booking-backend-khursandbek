"""
URL configuration for venues app.
"""

from django.urls import path

from .views import VenueAvailabilityView, VenueDetailView, VenueListView

urlpatterns = [
    path("", VenueListView.as_view(), name="venue-list"),
    path("<int:pk>/", VenueDetailView.as_view(), name="venue-detail"),
    path("<int:pk>/availability/", VenueAvailabilityView.as_view(), name="venue-availability"),
]
