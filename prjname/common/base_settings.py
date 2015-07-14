"""
Base settings used in all environments
"""
import datetime
import os

from prjname.common import settings

APPLICATION_ID = '1'

AUTO_RELOAD = False
ENFORCE_POLICIES = True
STATS_ENABLED = False

JWT_TOKEN_NOT_BEFORE_TIMEDELTA = datetime.timedelta(minutes=1)

LOG_DIR = os.path.expanduser("~")
LOGGER_NAME = 'service'
ANALYTICS_LOGGER_NAME = 'analytics'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(thread)d %(env)s %(service)s %(handler)s %(requestId)s '
                      '%(message)s'
        },
        'analytics': {
            'format': '%(asctime)s %(env)s %(service)s %(handler)s %(app)s %(account)s %(user)s %(device)s'
        }
    },
    'handlers': {
        'local_internal': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'prjname_service.log'),
            'formatter': 'verbose'
        },
        'local_analytics': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'prjname_analytics.log'),
            'formatter': 'analytics'
        },
    },
    'loggers': {
        LOGGER_NAME: {
            'handlers': ['local_internal'],
            'level': 'DEBUG',
            'propagate': True,
        },
        ANALYTICS_LOGGER_NAME: {
            'handlers': ['local_analytics'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

JSON_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'json_schema', 'schemas')
JSON_SCHEMA_BASE_URL = "http://prjname/jsonschema/"

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
