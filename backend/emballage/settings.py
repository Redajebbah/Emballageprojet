from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import os
from urllib.parse import urlparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-default-dev-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']  # You can replace '*' with your Render domain later

# If running behind Render (or another proxy) so request.is_secure() works
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF and CORS — configure via environment variables in production
# Example env values: 'https://emboitage.com,https://www.emboitage.com'
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://emboitage.com,https://www.emboitage.com'
).split(',')

# If you install django-cors-headers, you can use this setting to allow
# the frontend (hosted on Vercel) to call the API.
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'https://emboitage.com,https://www.emboitage.com'
).split(',')

# Applications
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'corsheaders',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'rest_framework',
    'categories',
    'adminpanel',
    'products',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # for serving static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'emballage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.contact_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'emballage.wsgi.application'

# WhatsApp number used by the "Demander un devis" buttons (international format, digits only)
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '212658283277')

# Database: PostgreSQL from DATABASE_URL (Neon in production).
# Without DATABASE_URL (local development) we fall back to SQLite.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
# Neon suspends idle databases: re-check persistent connections before reuse.
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JS, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Compatibility fix for django-cloudinary-storage (required)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Media storage: uploaded photos go to Cloudinary when CLOUDINARY_URL is set
# (format: cloudinary://<api_key>:<api_secret>@<cloud_name>), otherwise to MEDIA_ROOT on disk.
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '').strip()
if CLOUDINARY_URL:
    _cloudinary = urlparse(CLOUDINARY_URL)
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': _cloudinary.hostname,
        'API_KEY': _cloudinary.username,
        'API_SECRET': _cloudinary.password,
        'SECURE': True,
    }
    _media_backend = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    CLOUDINARY_STORAGE = {}
    _media_backend = "django.core.files.storage.FileSystemStorage"

STORAGES = {
    "default": {
        "BACKEND": _media_backend,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
