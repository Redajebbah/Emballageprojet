from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import os
import dj_database_url
import cloudinary.utils

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
                'products.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'emballage.wsgi.application'

# Database (from Render environment variable)
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
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

# Cloudinary Storage Configuration
# Using official SDK util to parse CLOUDINARY_URL and ensure clean, synced credentials
_curl = os.environ.get('CLOUDINARY_URL', '').strip()
if _curl:
    _c = cloudinary.utils.config_from_url(_curl)
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': _c.cloud_name,
        'API_KEY': _c.api_key,
        'API_SECRET': _c.api_secret,
        'SECURE': True,
    }
    # Sync the base library config to match the storage backend
    cloudinary.config(
        cloud_name=_c.cloud_name,
        api_key=_c.api_key,
        api_secret=_c.api_secret,
        secure=True
    )
else:
    # Minimal fallback
    CLOUDINARY_STORAGE = {}

# Modern Django Storage Configuration (Django 4.2+)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}