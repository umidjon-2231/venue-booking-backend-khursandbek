"""
Custom permissions for the venue-booking-backend project.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    Assumes the model instance has a `user` attribute.
    """
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to any request,
    but only allow write access to admin users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users to access the view.
    """
    message = "Your account is not verified."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
