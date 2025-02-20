"""
Django settings for FindUS_Backend project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv  # Para cargar variables de entorno
from datetime import timedelta
import sys

# AppConfig.default = False
# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Append the path of the "apps" folder to sys.path so that the apps can be imported correctly.
APPS_DIR = os.path.join(BASE_DIR, "apps")
sys.path.append(APPS_DIR)

# Cargar variables de entorno desde el archivo correspondiente
env_file = BASE_DIR / f".env.{os.getenv('DJANGO_ENV', 'local')}"
load_dotenv(dotenv_path=env_file)


# Función para obtener variables de entorno
def getenv(name: str, default=None):
    if default is None and name not in os.environ:
        raise ValueError(f"Missing environment variable: {name}")

    return os.getenv(name, default)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Se sobreescribirá en los archivos de entorno

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    # Aplicaciones locales
    'users.apps.UsersConfig',
    'stores.apps.StoresConfig',
    'events.apps.EventsConfig',

    # Aplicaciones de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',  # JWT para autenticación
    'drf_spectacular',
]

# Configuración de REST Framework y autenticación con JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuración de SimpleJWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DJANGO_SETTINGS_MODULE = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.local')

# Database (Se sobreescribirá en entornos específicos)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración de internacionalización
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Configuración de archivos estáticos y de usuario
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Frontend en React local
    "https://find-us-jet.vercel.app"  # Frontend de vercel en producción
]
CORS_ALLOW_CREDENTIALS = True  # Permitir credenciales (cookies, tokens)

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'users.User'  # Solo si usas un modelo personalizado

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SPECTACULAR_SETTINGS = {
    "TITLE": "FindUD BACKEND API",
    "DESCRIPTION": "ENGINE BEHIND OUR SYSTEM",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        # "displayOperationId": True,
    },
}
