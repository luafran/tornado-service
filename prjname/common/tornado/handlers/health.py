"""
Tornado handler for health resource
"""
import json
from tornado import gen
from prjname.common.tornado.handlers import base

from prjname.common import exceptions
from prjname.common.health.health_monitor import HealthMonitor


HEALTH_MONITOR = HealthMonitor()


# pylint: disable=too-many-public-methods
class HealthHandler(base.BaseHandler):
    """
    Tornado handler for health resource
    """

    LOG_TAG = '[Health Handler] %s'

    # RequestHandler interface

    @gen.coroutine
    def get(self):
        """
        /health GET handler
        """
        health_criteria = self.request.query
        service_health = False
        version = None
        try:
            service_health, result, version = yield HEALTH_MONITOR.get_status(
                health_criteria.get('include_details'))
        except exceptions.InfoException as ex:
            message = 'error while getting health status'
            self.support.notify_error(self.LOG_TAG % message)
            result = ex
        except Exception as ex:  # pylint: disable=W0703
            message = 'error while getting health status'
            self.support.notify_error(self.LOG_TAG % message)
            result = ex

        self.build_health_response(service_health, result, version)

    # Helper methods

    def process_query(self, supported_query_attributes=('include_details',
                                                        '_')):
        """
        Validates the query parameters.
        """
        super(HealthHandler, self).process_query(supported_query_attributes)
        processed_query = self.request.arguments

        # include_details parameter validation
        include_details = 'include_details'
        try:
            value = processed_query[include_details][0].lower().title()
            if value not in ['True', 'False']:
                raise exceptions.InvalidArgument(
                    'include_details must be true or false')

            processed_query[include_details] = \
                True if value == 'True' else False

        except KeyError:
            pass    # include_details is not a query parameter

        self.request.query = processed_query

    def build_health_response(self, service_health, result, version,
                              status_code=None):
        """
        Build the health response data with the required format
        according to result
        """
        request_method = self.request.method
        self.set_header("Content-Type", "application/json")

        if isinstance(result, Exception):
            response_body = self._build_response_from_exception(result)
            self.write(response_body)
        else:
            response_body = {"status": {"health": service_health,
                                        "info": result,
                                        "version": version}}

            if request_method == 'GET':
                self.set_status(status_code if status_code else 200)
                self.write(json.dumps(response_body))

        self.finish()
