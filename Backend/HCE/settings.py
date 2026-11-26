import hashlib
import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_ENV = BASE_DIR / '.env'
if ARCHIVO_ENV.exists():
    load_dotenv(ARCHIVO_ENV)


def _obtener_clave(nombre_variable,nombre_archivo,generar):
    """Lee una clave del entorno o la genera una vez para desarrollo local."""
    valor = os.getenv(nombre_variable,'').strip()
    if valor:
        return valor
    ruta = BASE_DIR / nombre_archivo
    if not ruta.exists():
        ruta.write_text(generar(),encoding='utf-8')
    return ruta.read_text(encoding='utf-8').strip()


DEBUG = os.getenv('DEBUG','False').strip().lower() in ('1','true','yes','si')
SECRET_KEY = _obtener_clave(
    'SECRET_KEY',
    '.secret_dev_key',
    lambda: secrets.token_urlsafe(64),
)
ALLOWED_HOSTS = [
    elemento.strip()
    for elemento in os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1,testserver').split(',')
    if elemento.strip()
]
CORS_ALLOWED_ORIGINS = [
    elemento.strip()
    for elemento in os.getenv(
        'CORS_ALLOWED_ORIGINS','http://localhost:4200,http://127.0.0.1:4200'
    ).split(',')
    if elemento.strip()
]
FERNET_KEY = _obtener_clave('FERNET_KEY','.fernet_dev_key',lambda: Fernet.generate_key().decode())
FIRMA_SALT = os.getenv('FIRMA_SALT','').strip() or hashlib.sha256(FERNET_KEY.encode()).hexdigest()
if not DEBUG:
    if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-'):
        raise ImproperlyConfigured('Configura un SECRET_KEY seguro antes de desplegar en producción.')
    if len(FERNET_KEY) < 44:
        raise ImproperlyConfigured('Configura una FERNET_KEY válida antes de desplegar en producción.')

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HCE.urls'

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

WSGI_APPLICATION = 'HCE.wsgi.application'
ASGI_APPLICATION = 'HCE.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.getenv('DB_NAME','db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
RENDERERES = ['rest_framework.renderers.JSONRenderer']
if DEBUG:
    RENDERERES.append('rest_framework.renderers.BrowsableAPIRenderer')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'historia.auditoria.manejador_excepciones',
    'DEFAULT_RENDERER_CLASSES': RENDERERES,
}

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000' if not DEBUG else '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hce-webhooks',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'general': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'consola': {
            'class': 'logging.StreamHandler',
            'formatter': 'general',
        },
    },
    'loggers': {
        'django': {'handlers': ['consola'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['consola'], 'level': 'WARNING', 'propagate': False},
        'historia': {'handlers': ['consola'], 'level': 'WARNING', 'propagate': False},
    },
}
