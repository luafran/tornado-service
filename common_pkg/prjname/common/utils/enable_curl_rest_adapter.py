"""
This enables CURL for the asynchronous REST Adapter
"""
from tornado import httpclient

PROXY = {}
try:
    # Remember that pycurl needs the libcurl dev packages of your distro
    import pycurl
    assert pycurl

    import os
    from six.moves.urllib.parse import urlparse  # pylint: disable=no-name-in-module

    proxy_env = os.environ.get('http_proxy')
    if proxy_env:
        parsed_proxy = urlparse(proxy_env)
        PROXY = {
            'proxy_host': parsed_proxy.hostname,
            'proxy_port': parsed_proxy.port
        }

    httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient")
except ImportError:
    pass
