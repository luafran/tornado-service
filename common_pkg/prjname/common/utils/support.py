"""
Generic (domain agnostic) stuff to support application
"""
import statsd

from prjname.common import constants
from prjname.common import settings


class Support(object):
    """
    Class used to notify events useful to support the application
    """

    def __init__(self, logger, session_info=None):
        """
        Initialize instance with a logger to be used, info related to the request and info related to
        the service
        """

        self._logger = logger

        if not session_info:
            session_info = {}

        environment = session_info.get('environment')

        self._extra = {
            'env': environment,
            'service': session_info.get('service'),
            'handler': session_info.get('handler'),
            'requestId': session_info.get('requestId', constants.NO_REQUEST_ID),
            'details': ''
        }

        self._stats_enabled = settings.STATS_ENABLED

        if self._stats_enabled:
            self._stats_client = statsd.StatsClient(host=settings.STATS_SERVICE_HOSTNAME,
                                                    port=8125, prefix='prjname.' + environment)

    def notify_critical(self, message, details=None):
        """Notify a critical event"""

        self._extra['details'] = details if details else message
        self._logger.critical(message, extra=self._extra)

    def notify_error(self, message, details=None):
        """Notify an error event"""

        self._extra['details'] = details if details else message
        self._logger.error(message, extra=self._extra)

    def notify_warning(self, message, details=None):
        """Notify a warning event"""

        self._extra['details'] = details if details else message
        self._logger.warning(message, extra=self._extra)

    def notify_info(self, message, details=None):
        """Notify an information event"""

        self._extra['details'] = details if details else message
        self._logger.info(message, extra=self._extra)

    def notify_debug(self, message, details=None):
        """Notify a debug event"""

        self._extra['details'] = details if details else message
        self._logger.debug(message, extra=self._extra)

    def stat_increment(self, stat, count=1, rate=1):
        if self._stats_enabled:
            self._stats_client.incr(stat, count, rate)

    def stat_decrement(self, stat, count=1, rate=1):
        if self._stats_enabled:
            self._stats_client.decr(stat, count, rate)

    def stat_gauge(self, stat, value, rate=1, delta=False):
        if self._stats_enabled:
            self._stats_client.gauge(stat, value, rate, delta)

    def stat_set(self, stat, value, rate=1):
        if self._stats_enabled:
            self._stats_client.set(stat, value, rate)
