"""
Base models for the venue-booking-backend project.
Contains abstract models and mixins used across multiple apps.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ActiveModel(models.Model):
    """
    Abstract base model that provides an 'is_active' field
    for soft delete functionality.
    """
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        abstract = True

    def deactivate(self):
        """Soft delete the model instance."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def activate(self):
        """Reactivate a soft-deleted model instance."""
        self.is_active = True
        self.save(update_fields=["is_active"])


class ActiveManager(models.Manager):
    """
    Manager that returns only active records by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AllObjectsManager(models.Manager):
    """
    Manager that returns all records including inactive ones.
    """
    pass
