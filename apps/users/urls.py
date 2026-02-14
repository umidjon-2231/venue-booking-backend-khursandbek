"""
URL configuration for users app.
"""

from django.urls import path

from .views import RefreshTokenView, SendOTPView, UserProfileView, VerifyOTPView

urlpatterns = [
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
