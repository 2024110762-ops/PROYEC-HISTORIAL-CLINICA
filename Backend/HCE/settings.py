import os
from pathlib import Path

from cryptography.fernet import Fernet
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def _obtener_valor(variable, archivo=None, generador=None):
    valor = os.getenv(variable, '').strip()
    if valor:
        return valor
    if archivo:
        ruta = BASE_DIR / archivo
        if ruta.exists():
            contenido = ruta.read_text(encoding='utf-8').strip()
            if contenido:
                return contenido
    return generador() if generador else ''


SECRET_KEY = _obtener_valor('SECRET_KEY', '.secret_dev_key', get_random_secret_key)
FERNET_KEY = _obtener_valor('FERNET_KEY', '.fernet_dev_key', lambda: Fernet.generate_key().decode())
FIRMA_SALT = _obtener_valor('FIRMA_SALT', '.firma_salt_dev_key', get_random_secret_key)

DEBUG = os.getenv('DEBUG', 'True').strip().lower() in ('1', 'true', 'yes', 'on')
ALLOWED_HOSTS = [ elemento.strip() for elemento in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if elemento.strip() ]
CORS_ALLOWED_ORIGINS = [ elemento.strip() for elemento in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:4200').split(',') if elemento.strip() ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'historia',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HCE.urls'
WSGI_APPLICATION = 'HCE.wsgi.application'

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
            ],
        },
    },
]

_nombre_base_datos = os.getenv('DB_NAME', 'db.sqlite3').strip() or 'db.sqlite3'
_ruta_base_datos = Path(_nombre_base_datos)
if not _ruta_base_datos.is_absolute():
    _ruta_base_datos = BASE_DIR / _ruta_base_datos

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(_ruta_base_datos),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'EXCEPTION_HANDLER': 'historia.auditoria.manejador_excepciones',
}

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
