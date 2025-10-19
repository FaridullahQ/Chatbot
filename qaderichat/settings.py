"""
Django settings for QaderiChat project.
Enhanced for OpenRouter integration, streaming support, and clean configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# 🔐 Load environment variables early
# ============================================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# ⚙️ Security & Debug
# ============================================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ============================================
# 🧠 Installed Apps
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'channels',

    # Local
    'chat',
]

# ============================================
# 🧱 Middleware
# ============================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================
# 🌐 URL and Template Configuration
# ============================================
ROOT_URLCONF = 'qaderichat.urls'

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

WSGI_APPLICATION = 'qaderichat.wsgi.application'
ASGI_APPLICATION = 'qaderichat.asgi.application'

# ============================================
# 🗃️ Database
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================
# 🔐 Password validation
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================
# 🌍 Internationalization
# ============================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================
# 🖼️ Static & Media
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# 🤖 AI Configuration
# ============================================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# ✅ Select AI provider (default to OpenRouter if available)
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter').lower()

# ✅ Tuning parameters for speed & quality
AI_MODEL = os.getenv('AI_MODEL', 'openai/gpt-3.5-turbo-0125')
AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.4'))
AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '400'))
AI_TOP_P = float(os.getenv('AI_TOP_P', '1.0'))

# ============================================
# 🪟 CORS settings
# ============================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# ============================================
# 📡 Channels configuration (WebSockets)
# ============================================
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.getenv('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}

# ============================================
# 💾 Session
# ============================================
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# ============================================
# 🧪 Developer Info (for debugging & startup logs)
# ============================================
if DEBUG:
    print(f"[✅ SETTINGS LOADED]")
    print(f"• AI_PROVIDER = {AI_PROVIDER}")
    print(f"• AI_MODEL = {AI_MODEL}")
    if OPENROUTER_API_KEY:
        print("🔐 OpenRouter API Key detected")
    if OPENAI_API_KEY:
        print("🔐 OpenAI API Key detected")
    if ANTHROPIC_API_KEY:
        print("🔐 Anthropic API Key detected")
