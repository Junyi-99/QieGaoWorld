"""
Django settings for QieGaoWorld project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mv*-vigv0d#(%*v#!$@2b*&8(dk%z0-%(_r8o%&kh8xuzs=@7%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'QieGaoWorld',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'QieGaoWorld.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'QieGaoWorld.view.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'QieGaoWorld.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'qiegaoshijie',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'web',
        'PASSWORD': 'CL0WDZeOOWJ4eiY8',
        'OPTIONS': {
          'autocommit': True,
        },
    }
}


# my.cnf
# [client]
# database = NAME
# user = USER
# password = PASSWORD
# default-character-set = utf8

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/var/www/static',
]

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')
FACE_ROOT = os.path.join(BASE_DIR, 'static\\media\\face')

DEFAULT_PERMISSIONS = '%police_cases_watch%police_cases_add%declaration_animals%declaration_buildings' \
                      '%declaration_watch% '
OP_PERMISSIONS = '%publish_announcement%announcement_delete%police_cases_watch%police_cases_add%police_cases_modify' \
                 '%declaration_animals%declaration_buildings%declaration_watch%declaration_animals_modify' \
                 '%declaration_buildings_modify%whitelist%'

DEFAULT_FACE = os.path.join(BASE_DIR, 'static\\media\\face\\default.jpg')
BUILDING_CONCEPT_ROOT = os.path.join(BASE_DIR, 'static/media/buildings/concept')
BUILDING_PLAN_ROOT = os.path.join(BASE_DIR, 'static/media/buildings/plan')
BUILDING_PERSPECTIVE_ROOT = os.path.join(BASE_DIR, 'static/media/buildings/perspective')

PROJECT_VERSION = '2.0 Beta (180725)'


