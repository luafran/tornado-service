"""
Asynchronous REST Adapter
"""
import json
import urllib

from tornado import gen
from tornado import httpclient

from prjname.common import constants
from prjname.common.utils import enable_curl_rest_adapter
from prjname.common.utils import dictionaries


class RestAdapter(object):
    """
    Asynchronous REST Adapter
    """

    LOG_TAG = '[REST Adapter] %s'

    # pylint: disable=too-many-arguments
    def __init__(self, endpoint, context, support, validate_certs=None, certs=None,
                 use_system_proxies=False):
        self._http_client = httpclient.AsyncHTTPClient()

        self._endpoint = endpoint.rstrip('/')
        self._validate_certs = (validate_certs if validate_certs is not None
                                else False)
        self._certs = certs
        self._use_system_proxies = use_system_proxies
        self._support = support
        self._request_id = context.request_id if context else None

    @gen.coroutine
    def post(self, path=None, headers=None, body=None, timeout=None):
        """
        Send a http POST request
        """

        response_code, response_body = yield self._request('POST', path, None,
                                                           headers, body,
                                                           timeout)
        raise gen.Return((response_code, response_body))

    @gen.coroutine
    def get(self, path=None, query=None, headers=None, timeout=None):
        """
        Send a http GET request
        """

        response_code, response_body = yield self._request('GET', path, query,
                                                           headers, None,
                                                           timeout)
        raise gen.Return((response_code, response_body))

    @gen.coroutine
    # pylint: disable=R0913
    def put(self, path=None, query=None, headers=None, body=None,
            timeout=None):
        """
        Send a http PUT request
        """

        response_code, response_body = yield self._request('PUT', path, query,
                                                           headers, body,
                                                           timeout)
        raise gen.Return((response_code, response_body))

    @gen.coroutine
    def delete(self, path=None, query=None, headers=None, timeout=None):
        """
        Send a http DELETE request
        """

        response_code, response_body = yield self._request('DELETE', path,
                                                           query, headers,
                                                           None, timeout)
        raise gen.Return((response_code, response_body))

    def _get_system_proxies(self):
        return (
            enable_curl_rest_adapter.PROXY if self._use_system_proxies else {})

    # pylint: disable=no-self-use
    def _create_request(self, *args, **kwargs):
        return httpclient.HTTPRequest(*args, **kwargs)

    @gen.coroutine
    # pylint: disable=R0913
    def _request(self, method, path, query, headers, body, timeout):
        """
        Send a http request
        """

        if not headers:
            headers = {}

        if self._request_id:
            headers[constants.REQUEST_ID_HTTP_HEADER] = self._request_id

        url = self._endpoint
        if path is not None:
            url = ('%s%s' % (url, path)).rstrip('/')
        if query is not None:
            url = ('%s?%s' % (url, urllib.urlencode(query)))

        request = self._create_request(url=url,
                                       method=method,
                                       headers=headers,
                                       body=body,
                                       connect_timeout=timeout,
                                       request_timeout=timeout,
                                       validate_cert=self._validate_certs,
                                       ca_certs=self._certs,
                                       **self._get_system_proxies())

        if self._support:
            self._support.notify_debug(
                self.LOG_TAG % ('request: %s %s' % (method, path)))
            self._support.notify_debug(
                self.LOG_TAG % ('request body: %s' % body))

        try:
            response = yield self._http_client.fetch(request,
                                                     raise_error=False)
        except httpclient.HTTPError as ex:
            response = dictionaries.DictAsObject(
                code=ex.code,
                body=json.dumps({"message": ex.message}))

        response_code = response.code
        response_body = response.body

        raise gen.Return((response_code, response_body))
