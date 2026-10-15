from .base import *  # noqa: F401,F403

DEBUG = False

# Allow Railway's auto-generated domain alongside any explicitly listed hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[]) + [  # noqa: F405
    ".up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
] + env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")  # noqa: F405
}

# Railway terminates SSL at the proxy; trust the forwarded protocol header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
