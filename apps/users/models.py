"""
User models for the venue-booking-backend project.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for phone number authentication.
    """
    
    def create_user(self, phone_number, name=None, **extra_fields):
        """
        Create and save a regular user with the given phone number.
        """
        if not phone_number:
            raise ValueError(_("Phone number is required"))
        
        user = self.model(phone_number=phone_number, name=name or "", **extra_fields)
        user.set_unusable_password()  # Users authenticate via OTP, not password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, name=None, password=None, **extra_fields):
        """
        Create and save a superuser with the given phone number.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        user = self.model(phone_number=phone_number, name=name or "", **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model with phone number authentication.
    """
    
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        unique=True,
        help_text=_("Format: +998XXXXXXXXX"),
    )
    name = models.CharField(_("name"), max_length=150, blank=True)
    
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    is_verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_("Designates whether this user has verified their phone number."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into admin site."),
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.phone_number
    
    def get_full_name(self):
        return self.name or self.phone_number
    
    def get_short_name(self):
        return self.name or self.phone_number
