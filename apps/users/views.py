"""
Views for users app.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    OTPVerifySerializer,
    PhoneNumberSerializer,
    TokenResponseSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import OTPService


class SendOTPView(APIView):
    """
    Send OTP to the provided phone number.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PhoneNumberSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent successfully"),
            400: OpenApiResponse(description="Invalid phone number"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="Send OTP",
        description="Send OTP to the provided phone number. OTP is valid for 5 minutes. "
                    "Maximum 3 requests per phone number per 10 minutes.",
    )
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data["phone_number"]
        OTPService.send_otp(phone_number)
        
        return Response(
            {"message": "OTP sent successfully", "phone_number": phone_number},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """
    Verify OTP and return JWT tokens.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Invalid OTP or phone number"),
        },
        summary="Verify OTP",
        description="Verify OTP and receive JWT access and refresh tokens. "
                    "Creates user if not exists.",
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]
        
        # Verify OTP
        OTPService.verify_otp(phone_number, otp)
        
        # Get or create user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"is_verified": True},
        )
        
        # Mark as verified if existing user
        if not created and not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    """
    Refresh access token using refresh token.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        request={"type": "object", "properties": {"refresh": {"type": "string"}}},
        responses={
            200: {"type": "object", "properties": {"access": {"type": "string"}}},
            401: OpenApiResponse(description="Invalid refresh token"),
        },
        summary="Refresh Token",
        description="Get a new access token using refresh token.",
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {"access": str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user's profile.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        responses={200: UserSerializer},
        summary="Get User Profile",
        description="Get current authenticated user's profile.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        summary="Update User Profile",
        description="Update current authenticated user's profile.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        """Disable PUT method, only PATCH allowed."""
        return Response(
            {"error": "Method not allowed. Use PATCH instead."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
