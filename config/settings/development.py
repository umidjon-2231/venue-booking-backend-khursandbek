"""
Django development settings for venue-booking-backend project.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = [
    "127.0.0.1",
]

# Email backend - console for development (OTP will be logged here)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/hour",
    "user": "10000/hour",
}

# More verbose logging for development
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405

# Use local memory cache if Redis is not available
import socket

def is_redis_available():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(("localhost", 6379))
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False

if not is_redis_available():
    CACHES = {  # noqa: F405
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
