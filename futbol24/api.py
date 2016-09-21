"""A library that provides a Python interface to the Futbol24 API"""

import json
import sys
import gzip
import requests

from models import Country

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

class Api(object):
    """A python interface into the Futbol24 API"""

    DEFAULT_CACHE_TIMEOUT = 60  # cache for 1 minute
    _API_REALM = 'Futbol24 API'

    def __init__(self,
                 input_encoding=None,
                 request_headers=None,
                 cache=DEFAULT_CACHE,
                 base_url=None,
                 user_agent=None,
                 add_compat_f24_headers=False,
                 use_gzip_compression=False,
                 debug_http=False,
                 timeout=None):

        self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
        self._use_gzip = use_gzip_compression
        self._debug_http = debug_http
        self._timeout = timeout
        self._cookies = {}

        self._initialize_default_parameters()
        self._initialize_request_headers(request_headers)
        self._initialize_user_agent(user_agent)
        self._initialize_f24_headers(add_compat_f24_headers)

        if base_url is None:
            self.base_url = 'http://api.futbol24.gluak.com'
        else:
            self.base_url = base_url

        if debug_http:
            import logging
            import http.client

            http.client.HTTPConnection.debuglevel = 1

            logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def _initialize_default_parameters(self):
        self._default_params = {}

    def _initialize_request_headers(self, request_headers):
        if request_headers:
            self._request_headers = request_headers
        else:
            self._request_headers = {}

    def _initialize_user_agent(self, user_agent=None):
        # TODO: Eventually we should consider setting user agent in more general way.
        # At this moment it is hardcoded to match Android user agent from official app.
        if user_agent is None:
            user_agent = 'Futbol24 1.9.1/26 (compatible)'

        self.set_user_agent(user_agent)

    def _initialize_f24_headers(self, add_compatibility_headers=False):
        """Set the F24 HTTP headers that will be sent to the server.
        They are required to allow authorization on server side.

        """
        self._cookies['F24-CC'] ='sk'

        if add_compatibility_headers:
            self._request_headers['F24_APP_VERSION'] = '1.9.1'
            self._request_headers['XUSER_LANGUAGE'] = 'slk'
            self._request_headers['F24_DEVICE_ID'] = 'androidTab'

    def set_user_agent(self, user_agent):
        """Override the default user agent.
        Args:
          user_agent:
            A string that should be send to the server as the user-agent.
        """
        self._request_headers['User-Agent'] = user_agent

    def get_countries(self):
        url = '%s/countries' % self.base_url

        return requests.get(url, headers=self._request_headers, cookies = self._cookies)

