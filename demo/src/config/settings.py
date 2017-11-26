# -*- coding: utf-8 -*-
import os
import datetime

from configurations import Configuration


class Base(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    SRC_DIR = os.path.dirname(os.path.dirname(__file__))

    @property
    def ROOT_DIR(self):
        return os.path.dirname(self.SRC_DIR)

    @property
    def BASE_DIR(self):
        return os.path.dirname(self.ROOT_DIR)

    SECRET_KEY = 'lq8v7*gueqc2#@4@e(geeszvf!std-@f-zj51-zs-1(uqh&fe2'

    DEBUG = True

    ALLOWED_HOSTS = ['*']

    # Application definition

    DJANGO_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

    THIRD_PARTY_APPS = [
        'django_extensions',
    ]

    # Apps specific for this project go here.
    LOCAL_APPS = [
        'account',
    ]

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.common.CommonMiddleware',
    ]

    ROOT_URLCONF = 'config.urls'

    @property
    def TEMPLATES(self):
        return [
            {
                # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
                'DIRS': [
                    os.path.realpath(os.path.join(self.ROOT_DIR, 'templates')),
                ],
                'OPTIONS': {
                    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
                    'debug': self.DEBUG,
                    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
                    # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
                    'loaders': [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ],
                    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django.template.context_processors.tz',
                        'django.contrib.messages.context_processors.messages',
                        # Your stuff: custom template context processors go here
                    ],
                },
            },
        ]

    WSGI_APPLICATION = 'config.wsgi.application'

    # Password validation
    # https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/1.10/topics/i18n/

    LANGUAGE_CODE = 'En'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    @property
    def LOCALE_PATHS(self):
        return (
            os.path.join(self.SRC_DIR, 'locale'),
        )

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.10/howto/static-files/

    STATIC_URL = '/static/'

    @property
    def STATIC_ROOT(self):
        return os.path.join(self.BASE_DIR, 'static')  # str(ROOT_DIR('../../static'))

    MEDIA_URL = "/media/"

    @property
    def MEDIA_ROOT(self):
        return os.path.join(self.BASE_DIR, 'media')  # str(ROOT_DIR('../../media'))

    DATABASES = {
        'default': {
            'ATOMIC_REQUESTS': False,
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rester',
            'PORT': 5432,
            'PASSWORD': 'rester',
            'HOST': 'localhost',
            'USER': 'rester',
        }
    }

    DJANGO_RESTER = {
        'RESTER_LOGIN_FIELD': 'email',
        'RESTER_TRY_RESPONSE_STRUCTURE': True,
        'RESTER_JWT': {
            'JWT_SECRET': 'ASD213zFlc9324dzmcz',
            'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300 * 60 * 24),
            'JWT_AUTH_HEADER_PREFIX': 'api',
            'JWT_ALGORITHM': 'HS256',
            'JWT_USE_REDIS': True,
            'JWT_PAYLOAD_LIST': ['email'],
        }
    }

    DJANGO_REDISER = {
        'REDIS_DB': 5,
    }


class Local(Base):
    DEBUG = True


class Prod(Base):
    DEBUG = False
