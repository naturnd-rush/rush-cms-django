import dj_database_url

from .settings import *

DEBUG = True

SECRET_KEY = "test-secret"

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://postgres:postgres@localhost:5432/test_db",
        conn_max_age=0,
    )
}

# Optional: speed up password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
