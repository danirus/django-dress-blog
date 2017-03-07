"""
Django settings for demo2 project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i0qz5^k5e%^!ye0#dty*3*$fv62(ivu*p&di4p1w!k25+t3@g5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]

SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'compressor',  # Compress CSS and JavaScript files.
    'constance',  # Live settings.
    'django_comments',
    'django_comments_xtd',
    'flatblocks_xtd',
    'haystack',
    'inline_media',
    'prosemirror',
    'sorl.thumbnail',
    'taggit',
    'taggit_templatetags2',

    'dress_blog',
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

ROOT_URLCONF = 'demo2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'constance.context_processors.config',
            ],
        },
    },
]

WSGI_APPLICATION = 'demo2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.'
             'UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'NumericPasswordValidator'}
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "startbootstrap-clean-blog", "vendor"),
]

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'


CONSTANCE_CONFIG = {
    'title': (
        "Blog title", _("Blog's name of title."), str
    ),
    'posts_in_index': (
        1, _("Number of visible posts in 3-columns layout front page."), int
    ),
    'stories_in_index': (
        5, _("Number of visible stories in 4-columns layout front page."), int
    ),
    'quotes_in_index': (
        5, _("Number of visible quotes in 4-columns layout front page."), int
    ),
    'diary_entries_in_index': (
        1, _("Number of visible days in diary in front page."), int
    ),
    'comments_in_index': (
        5, _("Number of visible comments in front page."), int
    ),
    'email_subscribe_url': (
        "", _("Subscribe via mail URL."), str
    ),
    'show_author': (
        False, _("Show author's full name along in posts."), bool
    ),
    'ping_google': (
        False, _("Notify Google on new submissions."), bool
    ),
    'excerpt_length': (
        500,
        _("Number of characters of the post body to "
          "display in RSS feeds and preview templates."),
        int
    ),
    'meta_author': (
        "", _("List of authors or company/organization's name."), str
    ),
    'meta_keyword': (
        "",
        _("List of keywords to help improve quality of search results."),
        str
    ),
    'meta_description': (
        "", _("What the blog is about. Topics, editorial line..."), str
    ),
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': ('haystack.backends.elasticsearch_backend.'
                   'ElasticsearchSearchEngine'),
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

DRESS_BLOG_UI_COLUMNS = 4
