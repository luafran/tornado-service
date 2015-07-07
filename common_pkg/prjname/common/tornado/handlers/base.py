"""
BaseHandler
"""
import collections
import json
import os
import sys

from logging import config
from logging import getLogger
from tornado import httpclient
from tornado import web

from prjname.common import constants
from prjname.common import exceptions
from prjname.common import settings
from prjname.common.utils.support import Support

METHODS = (OPTIONS, GET, POST, PUT, DELETE, HEAD, PATCH) = (
    'OPTIONS', 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH'
)


class BaseHandler(web.RequestHandler):  # pylint: disable=too-many-public-methods
    """
    BaseHandler
    """
    def __init__(self, application, request, **kwargs):
        """
        Constructor
        """
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.context = None

    def data_received(self, chunk):
        pass

    def initialize(self, application_settings, handler=None):  # pylint: disable=arguments-differ
        self.application_settings = application_settings
        self.handler = handler
        self.request_id = self.request.headers.get(constants.REQUEST_ID_HTTP_HEADER)

        config.dictConfig(settings.LOGGING)
        logger = getLogger(settings.LOGGER_NAME)

        environment_name = 'MFS_ENV'

        environment = os.environ.get(environment_name)
        if not environment:
            raise exceptions.GeneralInfoException(
                '{0} environment variable not found'.format(environment_name))
        self.environment = environment

        session_info = {
            'environment': environment,
            'service': self.settings.get('service_name'),
            'handler': handler,
            'requestId': self.request_id
        }
        self.support = Support(logger, session_info)

        self.resource_name = "{0}_{1}".format(session_info['service'],
                                              handler if handler else '')

    def prepare(self):
        """
        Called at the beginning of a request before get/post/etc.
        Override this method to perform common initialization regardless of the
        request method
        """

        try:
            self.process_query()
            self.process_headers()
            self.process_body()

            request = self.request

            self.support.notify_debug(
                "[BaseHandler] request: %s %s" % (str(request.method), str(request.uri)))
            self.support.notify_debug(
                "[BaseHandler] query: %s" % str(request.query))
            self.support.notify_debug(
                "[BaseHandler] headers: %s" % str(request.headers))
            self.support.notify_debug(
                "[BaseHandler] body: %s" % str(request.body))

            body_size = sys.getsizeof(request.body)
            self.support.stat_increment('net.requests.total_count')
            self.support.stat_increment('net.requests.total_bytes', body_size)
            self.support.stat_increment('net.requests.' + str(request.method) + '_count')
            self.support.stat_increment('net.requests.' + str(request.method) + '_bytes', body_size)

        except exceptions.InfoException as ex:
            self.support.notify_error(ex)
            self.build_response(ex)
        except Exception as ex:  # pylint: disable=W0703
            self.support.notify_error(ex)
            self.build_response(ex)

    def set_default_headers(self):
        self.set_header("Server", "Miramar Web Server")
        self.set_header('Access-Control-Allow-Headers', 'Authorization, '
                        + 'Content-Type, ' + constants.REQUEST_ID_HTTP_HEADER)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Max-Age', '1728000')

    def process_headers(self, required_headers=None):
        """
        Process the request headers to validate if the headers in required_headers
        come in the request.
        Overwrite this method to extend this behavior or to change it at all.
        """

        if required_headers is None:
            required_headers = []
        else:
            pass

        if (self.request.method == 'POST') or (self.request.method == 'PUT'):
            required_headers.append('Content-Type')
        else:
            pass

        missing_headers = []
        for header in required_headers:
            if self.request.headers.get(header) is None:
                missing_headers.append(header)
            else:
                pass

        if len(missing_headers):
            raise exceptions.MissingArgumentValue('these headers are required: %s' %
                                                  missing_headers)
        else:
            pass

    def process_query(self, supported_query_attributes=None):
        """
        Process the request query.
        Overwrite this method to extend this behavior or to change it at all.
        """
        if supported_query_attributes:
            processed_query = self.request.arguments
            unsupported_attributes = list(
                set(processed_query.keys()) - set(supported_query_attributes))
            if unsupported_attributes:
                raise exceptions.InvalidArgument(
                    'The following query parameters are not supported: %s' %
                    unsupported_attributes)

    def process_body(self):
        """
        Process the request body to validate if it is valid based on the
        Content-Type header.
        Overwrite this method to extend this behavior or to change it at all.
        """

        body = self.request.body
        method = self.request.method

        if method == 'POST' or method == 'PUT':
            content_type = self.request.headers.get('Content-Type')

            if content_type.startswith('application/json'):
                try:
                    processed_body = json.loads(
                        body, object_pairs_hook=collections.OrderedDict)
                except (TypeError, ValueError) as ex:
                    raise exceptions.InvalidArgument('invalid body: %s' % ex)
            else:
                processed_body = self.request.arguments
        else:
            processed_body = None

        self.request.body_arguments = processed_body

    def build_response(self, result, status_code=None):
        """
        Build the response data with the required format according to result
        """
        self._build_response_internal(True, result, status_code)

    def build_response_without_format(self, result, status_code=None):
        """
        Build the response data with the required format according to result
        """
        self._build_response_internal(False, result, status_code)

    def _build_response_internal(self, apply_format, result, status_code=None):
        """
        Build the response data with the required format according to result
        """

        if apply_format:
            self.set_header("Content-Type", "application/json")

        if isinstance(result, Exception):
            body = self._build_response_from_exception(result)
            self.write(body)
        else:
            if apply_format:
                body = json.dumps(result)
            else:
                body = result

            if self.request.method == 'GET':
                self.set_status(status_code if status_code is not None else 200)
                self.write(body)
            elif self.request.method == 'POST':
                self.set_status(status_code if status_code is not None else 201)
                self.write(body)
            elif self.request.method == 'PUT':
                self.set_status(status_code if status_code is not None else 204)
            elif self.request.method == 'DELETE':
                self.set_status(status_code if status_code is not None else 200)
            else:
                pass

        if self.request_id:
            self.set_header(constants.REQUEST_ID_HTTP_HEADER, self.request_id)

        self.support.stat_increment('net.responses.total_count')
        self.support.stat_increment('net.responses.total_bytes', sys.getsizeof(body))

        self.finish()

    def _build_response_from_exception(self, ex):
        """
        Build HTTP response from an exception
        """
        if isinstance(ex, exceptions.BadRequestBase):
            self.set_status(400)
            response_body = str(ex)
        elif isinstance(ex, exceptions.UnauthorizedBase):
            self.set_status(401)
            response_body = str(ex)
        elif isinstance(ex, exceptions.ForbiddenBase):
            self.set_status(403)
            response_body = str(ex)
        elif isinstance(ex, exceptions.NotFoundBase):
            self.set_status(404)
            response_body = str(ex)
        elif isinstance(ex, exceptions.PermanentServiceError):
            self.set_status(500)
            response_body = str(ex)
        elif isinstance(ex, exceptions.TemporaryServiceError):
            self.set_status(503)
            response_body = str(ex)
        elif isinstance(ex, web.HTTPError):
            self.set_status(ex.status_code)
            response_body = {"message": str(ex)}
        elif isinstance(ex, httpclient.HTTPError):
            self.set_status(ex.code)
            response_body = {"message": ex.message}
        else:
            self.set_status(500)
            import traceback
            formatted_lines = traceback.format_exc().splitlines()
            ex = exceptions.GeneralInfoException(formatted_lines[-1])
            response_body = str(ex)

        return response_body

    def options(self, *args, **kwargs):
        options_list = [OPTIONS]

        if self.__class__.get != BaseHandler.get:
            options_list.append(GET)

        if self.__class__.post != BaseHandler.post:
            options_list.append(POST)

        if self.__class__.put != BaseHandler.put:
            options_list.append(PUT)

        if self.__class__.delete != BaseHandler.delete:
            options_list.append(DELETE)

        if self.__class__.head != BaseHandler.head:
            options_list.append(HEAD)

        if self.__class__.patch != BaseHandler.patch:
            options_list.append(PATCH)

        self.set_header('Access-Control-Allow-Methods',
                        ', '.join(options_list))


class Context(object):  # pylint: disable=too-many-instance-attributes
    """
    Context
    """

    def __init__(self, request):
        """
        Constructor
        """
        self.account_id = None
        self.client_id = None
        self.device_id = None
        self.member_id = None
        self.role = None
        self.products = None
        self.token = None

        self.request_id = request.headers.get(constants.REQUEST_ID_HTTP_HEADER)

        token = getattr(request, 'token', None)
        self.update_from_token(token)

    def update_from_token(self, token):
        if token:
            self.account_id = token.payload.get(constants.ACCOUNT_ID)
            self.client_id = token.payload.get(constants.CLIENT_ID)
            self.device_id = token.payload.get(constants.DEVICE_ID)
            self.member_id = token.payload.get(constants.MEMBER_ID)
            self.role = token.payload.get(constants.ROLE)
            self.products = token.payload.get(constants.PRODUCTS)
            self.products = self.products.split(',') if self.products else []
            self.token = token.token if token.token else None

    def get_owner(self):
        return {
            'owner': {
                'applicationId': self.client_id,
                'userId': self.account_id,
                'memberId': self.member_id,
                'deviceId': self.device_id
            }
        }
