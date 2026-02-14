"""
Django production settings for venue-booking-backend project.
Security-hardened configuration for deployment.
"""

from decouple import Csv, config

from .base import *  # noqa: F401, F403

# =============================================================================
# Core Settings
# =============================================================================
DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# =============================================================================
# Security Settings
# =============================================================================

# XSS Protection
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Clickjacking Protection
X_FRAME_OPTIONS = "DENY"

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookie Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Content Security Policy (via middleware if needed)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# =============================================================================
# Database Connection Pooling
# =============================================================================
DATABASES["default"]["CONN_MAX_AGE"] = config("DB_CONN_MAX_AGE", default=60, cast=int)  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405

# =============================================================================
# Caching (Enhanced for Production)
# =============================================================================
CACHES["default"]["OPTIONS"]["SOCKET_CONNECT_TIMEOUT"] = 5  # noqa: F405
CACHES["default"]["OPTIONS"]["SOCKET_TIMEOUT"] = 5  # noqa: F405

# =============================================================================
# Rate Limiting (Stricter in Production)
# =============================================================================
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "50/hour",
    "user": "500/hour",
}

# =============================================================================
# Logging (Production)
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {module} {process:d} {thread:d} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# Admin Security
# =============================================================================
ADMIN_URL = config("ADMIN_URL", default="admin/")

# =============================================================================
# Email Configuration (for error notifications)
# =============================================================================
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
SERVER_EMAIL = config("SERVER_EMAIL", default="noreply@example.com")
ADMINS = [
    (config("ADMIN_NAME", default="Admin"), config("ADMIN_EMAIL", default="")),
]
