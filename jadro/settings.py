import os
SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TOP_DIR, 'default.db'),
        },
    'contacts': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/data/com.android.providers.contacts/databases/contacts2.db',
        },
    }
from jadro_inspect import DROID_DATABASES
DATABASES.update(DROID_DATABASES)

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

def generate_secret_key():
    # taken from Django core/management/commands/startproject.py
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)

def create_secret_file(secret_file_name):
    with open(os.path.join(SETTINGS_DIR, secret_file_name), 'w') as secret_file:
        secret_file.write("SECRET_KEY = '%s'\n" % generate_secret_key())

# http://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys
try:
    from jadro.secret_key import SECRET_KEY
except ImportError:
    create_secret_file('secret_key.py')
    from jadro.secret_key import SECRET_KEY
  
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'jadro.urls'
WSGI_APPLICATION = 'jadro.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SETTINGS_DIR, 'templates'),
)

from jadro_inspect import INSTALLED_APPS as DROID_INSTALLED_APPS
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.databrowse',
    'django.contrib.admin',
    'jadro_contacts',
) + DROID_INSTALLED_APPS

DATABASE_ROUTERS = [ 'jadro_inspect.Router', 'jadro_contacts.Router' ]
