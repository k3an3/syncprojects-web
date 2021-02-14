from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

TIME_ZONE = 'EST'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
#STATIC_ROOT = BASE_DIR / "staticfiles"

INTERNAL_IPS = [
    '127.0.0.1',
]
