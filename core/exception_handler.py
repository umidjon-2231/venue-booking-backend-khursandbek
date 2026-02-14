"""
Custom exception handlers for the venue-booking-backend project.
Provides consistent error response format across all endpoints.
"""

import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error format.
    
    Response format:
    {
        "error": {
            "code": "error_code",
            "message": "Human readable message",
            "details": {...}  # Optional, for validation errors
        }
    }
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)
    
    # Log the exception
    request = context.get("request")
    view = context.get("view")
    
    if response is None:
        # Handle non-DRF exceptions
        if isinstance(exc, Http404):
            response = Response(
                {
                    "error": {
                        "code": "not_found",
                        "message": "The requested resource was not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        elif isinstance(exc, PermissionDenied):
            response = Response(
                {
                    "error": {
                        "code": "permission_denied",
                        "message": "You do not have permission to perform this action.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        elif isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Validation error occurred.",
                        "details": exc.message_dict if hasattr(exc, "message_dict") else str(exc),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Log unexpected exceptions
            logger.exception(
                f"Unhandled exception in {view.__class__.__name__}: {exc}",
                extra={
                    "request_path": request.path if request else None,
                    "request_method": request.method if request else None,
                },
            )
            response = Response(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred. Please try again later.",
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        # Format DRF exceptions consistently
        if isinstance(exc, DRFValidationError):
            response.data = {
                "error": {
                    "code": "validation_error",
                    "message": "Validation error occurred.",
                    "details": response.data,
                }
            }
        elif isinstance(exc, APIException):
            response.data = {
                "error": {
                    "code": getattr(exc, "default_code", "api_error"),
                    "message": str(exc.detail) if hasattr(exc, "detail") else str(exc),
                }
            }
    
    # Add request ID if available (useful for debugging)
    if response is not None and hasattr(request, "request_id"):
        response.data["error"]["request_id"] = request.request_id
    
    return response
