"""
Django Security Lab - config/settings.py
========================================
INTENTIONAL VULNERABILITIES:
  [V-01] DEBUG = True  leaks stack traces, SQL, env vars to the browser
  [V-02] SECRET_KEY is hardcoded (should come from env / secrets manager)
  [V-03] ALLOWED_HOSTS = ['*'] accepts requests from any host (Host-header injection)
  [V-04] Password validators disabled  → weak/empty passwords accepted
  [V-05] X_FRAME_OPTIONS not set      → clickjacking possible
  [V-06] SECURE_* flags all off       → cookies sent over plain HTTP
  [V-07] MEDIA files served directly  → no access-control on uploads
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── [V-01] Debug mode ON ──────────────────────────────────────────────────────
# Full stack traces, SQL queries, and local variables exposed in the browser.
DEBUG = True

# ── [V-02] Hardcoded secret key ───────────────────────────────────────────────
# Anyone who reads the source code (e.g. via a public repo) can forge sessions,
# CSRF tokens, and signed cookies.
SECRET_KEY = "django-insecure-lab-secret-1234567890abcdefghij"

# ── [V-03] Wildcard allowed hosts ─────────────────────────────────────────────
ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "accounts.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "profiles",
    "feedback",
    "documents",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ── CSRF middleware is present but views selectively disable it via
    #    @csrf_exempt – see feedback/views.py and dashboard/views.py
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # ── [V-05] XFrameOptionsMiddleware intentionally removed ──────────────────
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── [V-04] All password validators removed ────────────────────────────────────
# Accepts passwords like "a", "1", or even an empty string via the API.
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ── [V-07] Media served with no access control ────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ── [V-06] Security headers all disabled ─────────────────────────────────────
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
