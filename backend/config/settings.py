"""Django settings with environment-based configuration.

Local dev defaults to SQLite so the project runs without extra services.
Set DATABASE_URL to use PostgreSQL (e.g. in Docker Compose / production).
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "practice",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES: list = []

WSGI_APPLICATION = "config.wsgi.application"

# Database: SQLite by default, PostgreSQL when DATABASE_URL is set.
# WAL journal mode and busy_timeout let the background evaluation thread
# read/write concurrently with the Django test client — no more SQLITE_BUSY.
_db_config = dj_database_url.config(
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    conn_max_age=600,
)
if _db_config.get("ENGINE") == "django.db.backends.sqlite3":
    _db_config.setdefault("OPTIONS", {})
    _db_config["OPTIONS"]["timeout"] = 20  # seconds before SQLITE_BUSY error
DATABASES = {"default": _db_config}


def _set_sqlite_wal(sender, connection, **kwargs):
    """Enable WAL mode + busy_timeout on every new SQLite connection."""
    if connection.vendor == "sqlite":
        connection.cursor().execute("PRAGMA journal_mode=WAL;")
        connection.cursor().execute("PRAGMA busy_timeout=20000;")


try:
    from django.db.backends.signals import connection_created
    connection_created.connect(_set_sqlite_wal)
except Exception:
    pass


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}

# CORS: frontend dev server origin(s). Comma-separated list.
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "0") == "1"

# Evaluation provider configuration. Rule-based evaluator is the default and
# works without any external key. Set LLM_* to enable the optional LLM path.
LLM_ENABLED = os.environ.get("LLM_ENABLED", "0") == "1"
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))

# Enforce HTTPS-only cookies/secure redirect in production (DEBUG=0).
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "1") == "1"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
