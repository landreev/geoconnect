"""Development settings and globals."""

from __future__ import absolute_import
import json
import sys
from os.path import join, normpath, isdir

from .base import *

# Store uploaded files, logs, etc, etc
TEST_SETUP_DIR = normpath(join(dirname(dirname(DJANGO_ROOT)), 'test_setup'))

####################### DATAVERSE_INFO_REPOSITORY_PATH
#
# Path to additional repository: https://github.com/IQSS/shared-dataverse-information
# Used for dataverse/worldmap communication.  Validate data passed via api, etc
#
DATAVERSE_INFO_REPOSITORY_PATH = '/Users/rmp553/Documents/iqss-git/shared-dataverse-information/'
if not isdir(DATAVERSE_INFO_REPOSITORY_PATH):
    raise Exception('Directory not found for repository "shared-dataverse-information" (https://github.com/IQSS/shared-dataverse-information)\ndirectory in settings: %s' % DATAVERSE_INFO_REPOSITORY_PATH)
sys.path.append(DATAVERSE_INFO_REPOSITORY_PATH)
####################### END: DATAVERSE_INFO_REPOSITORY_PATH


STATIC_ROOT =join(TEST_SETUP_DIR, 'assets') # where files gathered and served from

MEDIA_ROOT = join(TEST_SETUP_DIR, 'media' )

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(TEST_SETUP_DIR, 'geodb.db3')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
   
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
    #'djcelery',
    #'kombu.transport.django', 
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

########## SESSION_COOKIE_NAME
SESSION_COOKIE_NAME = 'geoconnect_dev'
########## END SESSION_COOKIE_NAME

########## LOGIN_URL
# To use with decorator @login_required
LOGIN_URL = "admin:index"
########## END LOGIN_URL



########### DIRECTORY TO STORE DATA FILES COPIES FROM DV
# Do NOT make this directory accessible to a browser
#
DV_DATAFILE_DIRECTORY = join(TEST_SETUP_DIR, 'dv_datafile_directory')

########## GISFILE_SCRATCH_WORK_DIRECTORY
# Used for opening up files for processing, etc
GISFILE_SCRATCH_WORK_DIRECTORY = join(TEST_SETUP_DIR, 'gis_scratch_work')
########## END GISFILE_SCRATCH_WORK_DIRECTORY

##### RETRIEVE WORLDMAP PARAMS
#worldmap_secrets_fname = join( dirname(abspath(__file__)), "worldmap_secrets_dev.json")
worldmap_secrets_fname = join( dirname(abspath(__file__)), "worldmap_secrets_dev.json")
worldmap_secrets_json = json.loads(open(worldmap_secrets_fname, 'r').read())

########## WORLDMAP TOKEN/SERVER | DATAVERSE TOKEN AND SERVER
#
WORLDMAP_TOKEN_FOR_DV = worldmap_secrets_json['WORLDMAP_TOKEN_FOR_DV']
WORLDMAP_SERVER_URL = worldmap_secrets_json['WORLDMAP_SERVER_URL']
##########  END WORLDMAP TOKEN / SERVER

########## DATAVERSE_SERVER_URL
# Used to make API calls
# e.g.  http://dvn-build.hmdc.harvard.edu/
#
DATAVERSE_TOKEN_KEYNAME = 'GEOCONNECT_TOKEN'
DATAVERSE_SERVER_URL = 'http://localhost:8080'
DATAVERSE_METADATA_UPDATE_API_PATH =  '/api/worldmap/update-layer-metadata/' #DATAVERSE_SERVER_URL + '/api/worldmap/layer-update/'
##########  END DATAVERSE_SERVER_URL


########## LOGGING

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(TEST_SETUP_DIR, 'logs', 'geolog.log'),
            'formatter': 'simple'
            },
        },
    'loggers': {
        '': {
               'handlers': ['console'],
               'level': 'ERROR',
               'propagate': True
           },
        '': {
               'handlers': ['console'],
               'level': 'DEBUG',
               'propagate': True
           },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
            },
        },
        'geoconnect': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
            },
    }
    
# make all loggers use the console.
#for logger in LOGGING['loggers']:
#   LOGGING['loggers'][logger]['handlers'] = ['console']
LOGGING['loggers']['']['handlers'] = ['console']
