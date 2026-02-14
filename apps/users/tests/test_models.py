"""
Tests for User model.
"""

import pytest

from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            phone_number="+998901234567",
            name="Test User",
        )
        
        assert user.phone_number == "+998901234567"
        assert user.name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_staff is False
        assert user.is_superuser is False
        assert not user.has_usable_password()
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            phone_number="+998909999999",
            name="Admin",
            password="adminpass",
        )
        
        assert user.phone_number == "+998909999999"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.has_usable_password()
    
    def test_create_user_without_phone_raises_error(self):
        """Test that creating user without phone number raises error."""
        with pytest.raises(ValueError, match="Phone number is required"):
            User.objects.create_user(phone_number="", name="Test")
    
    def test_phone_number_is_unique(self, user):
        """Test that phone number must be unique."""
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                phone_number=user.phone_number,
                name="Another User",
            )
    
    def test_str_representation(self, user):
        """Test string representation of user."""
        assert str(user) == user.phone_number
    
    def test_get_full_name(self, user):
        """Test get_full_name method."""
        assert user.get_full_name() == user.name
    
    def test_get_full_name_without_name(self):
        """Test get_full_name returns phone when name is empty."""
        user = User.objects.create_user(phone_number="+998902222222")
        assert user.get_full_name() == user.phone_number
    
    def test_get_short_name(self, user):
        """Test get_short_name method."""
        assert user.get_short_name() == user.name
