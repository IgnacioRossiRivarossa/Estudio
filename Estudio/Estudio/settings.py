import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-cambiar-en-produccion')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'django_cleanup.apps.CleanupConfig',  # Debe ir último según documentación
]

LOCAL_APPS = [
    'usuarios.apps.UsuariosConfig',
    'clientes.apps.ClientesConfig',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# Whitenoise solo en producción
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'Estudio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Estudio.wsgi.application'
ASGI_APPLICATION = 'Estudio.asgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL', default=''),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

AUTH_USER_MODEL = 'usuarios.Usuario'

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.EmailBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'usuarios.validators.MayusculaValidator',
    },
    {
        'NAME': 'usuarios.validators.NumeroValidator',
    },
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Formato de fecha y hora en español
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

if DEBUG:
    # En desarrollo: configuración estándar de Django
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    # En producción: Whitenoise con compresión
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp-mail.outlook.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=5, cast=int)  # Timeout reducido a 5 segundos
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@estudio.com')

# En desarrollo, usar backend de consola si no hay credenciales SMTP
if DEBUG and not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'estudio-cache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'estudio-cache',
            # TODO: Configurar Redis o Memcached en producción cuando se requiera
            # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            # 'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        }
    }

if not DEBUG:
    # HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # Orígenes de confianza para CSRF (requerido en Django 4.x+ con HTTPS)
    CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Protección de contenido (SECURE_BROWSER_XSS_FILTER eliminado en Django 4.0)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import logging as _logging
_render_logger = _logging.getLogger(__name__)

if 'RENDER' in os.environ:
    _render_logger.info('Usando configuración de Render.com')

    # Desactivar DEBUG en producción
    DEBUG = False

    # Configurar hosts permitidos desde variable de entorno
    _render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if _render_hostname:
        ALLOWED_HOSTS = [_render_hostname]
    
    # Configurar base de datos PostgreSQL desde DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Asegurar que Whitenoise esté en MIDDLEWARE para servir archivos estáticos
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
            'whitenoise.middleware.WhiteNoiseMiddleware'
        )
    
    # Configurar directorio de archivos estáticos para producción
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Usar compresión Brotli para archivos estáticos
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'clientes': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
