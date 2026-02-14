"""
Serializers for users app.
"""

from rest_framework import serializers

from core.utils import validate_uzbekistan_phone

from .models import User


class PhoneNumberSerializer(serializers.Serializer):
    """
    Serializer for phone number input (send OTP).
    """
    
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        """Validate Uzbekistan phone number format."""
        if not validate_uzbekistan_phone(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Expected: +998XXXXXXXXX"
            )
        return value


class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer for OTP verification.
    """
    
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_phone_number(self, value):
        """Validate Uzbekistan phone number format."""
        if not validate_uzbekistan_phone(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Expected: +998XXXXXXXXX"
            )
        return value
    
    def validate_otp(self, value):
        """Validate OTP is numeric."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    
    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "name",
            "is_active",
            "is_verified",
            "created_at",
        )
        read_only_fields = ("id", "phone_number", "is_active", "is_verified", "created_at")


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    
    class Meta:
        model = User
        fields = ("name",)


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response (documentation purposes).
    """
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
