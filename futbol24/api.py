"""A library that provides a Python interface to the Futbol24 API"""

import json
from urllib.parse import urlparse, urlunparse, urlencode

import requests

from futbol24 import Country, Team
from futbol24.error import Futbol24Error

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
                 debug_http=False,
                 timeout=None):

        self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
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

        self._request_headers['Accept'] = 'application/json'

    def _initialize_user_agent(self, user_agent=None):
        if user_agent is None:
            user_agent = 'Futbol24 1.9.1/26 (compatible)'

        self.set_user_agent(user_agent)

    def _initialize_f24_headers(self, add_compatibility_headers=False):
        """Set the F24 HTTP headers that will be sent to the server.
        They are required to allow authorization on server side.

        """
        self._cookies['F24-CC'] = 'sk'

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

    def get_countries(self, filter_by_tables=False):
        # Build request parameters
        parameters = {}

        if filter_by_tables:
            parameters['filter'] = 'tables'

        url = '%s/countries' % self.base_url

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_json_data(resp.content.decode('utf-8'))
        return [Country.new_from_json_dict(x) for x in data.get('countries', '')['list']]

    def get_teams(self, country_id):
        try:
            if int(country_id) < 0:
                raise Futbol24Error({'message': "'country_id' must be a positive number"})
        except ValueError:
            raise Futbol24Error({'message': "'country_id' must be an integer"})

        # Build request parameters
        parameters = {}

        url = '{0}/country/{1}/teams'.format(self.base_url, country_id)

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_json_data(resp.content.decode('utf-8'))
        return [Team.new_from_json_dict(x) for x in data.get('teams', '')['list']]

    def _request_url(self, url, method, data=None, json=None):
        """Request a url.
        Args:
            url:
                The web location we want to retrieve.
            method:
                Either POST or GET.
            data:
                A dict of (str, unicode) key/value pairs.
        Returns:
            A JSON object.
        """

        if method == 'POST':
            if data:
                resp = requests.post(url, headers=self._request_headers, cookies=self._cookies,
                                     data=data, timeout=self._timeout)
            elif json:
                self._request_headers['Content-Type'] = 'application/json'
                resp = requests.post(url, headers=self._request_headers, cookies=self._cookies,
                                     json=json, timeout=self._timeout)
            else:
                resp = 0  # POST request, but without data or json

        elif method == 'GET':
            url = self._build_url(url, extra_params=data)
            resp = requests.get(url, headers=self._request_headers, cookies=self._cookies, timeout=self._timeout)

        else:
            resp = 0  # if not a POST or GET request

        return resp

    def _build_url(self, url, path_elements=None, extra_params=None):
        # Break url into constituent parts
        (scheme, netloc, path, params, query, fragment) = urlparse(url)

        # Add any additional path elements to the path
        if path_elements:
            # Filter out the path elements that have a value of None
            p = [i for i in path_elements if i]
            if not path.endswith('/'):
                path += '/'
            path += '/'.join(p)

        # Add any additional query parameters to the query string
        if extra_params and len(extra_params) > 0:
            extra_query = self._encode_parameters(extra_params)
            # Add it to the existing query
            if query:
                query += '&' + extra_query
            else:
                query = extra_query

        # Return the rebuilt URL
        return urlunparse((scheme, netloc, path, params, query, fragment))

    def _parse_and_check_json_data(self, json_data):
        """Try and parse the JSON returned from Futbol24 and return
        an empty dictionary if there is any error.
        """
        data = None
        try:
            data = json.loads(json_data)

        except:
            if "Error 403 Forbidden" in json_data:
                raise Futbol24Error({'message': "Forbidden"})
            if "404 Not Found" in json_data:
                raise Futbol24Error({'message': "Not Found"})

        return data

    def _encode_parameters(self, parameters):
        """Return a string in key=value&key=value form.
        Values of None are not included in the output string.
        Args:
          parameters (dict): dictionary of query parameters to be converted into a
          string for encoding and sending to Twitter.
        Returns:
          A URL-encoded string in "key=value&key=value" form
        """
        if parameters is None:
            return None
        if not isinstance(parameters, dict):
            raise Futbol24Error("`parameters` must be a dict.")
        else:
            return urlencode(dict((k, v) for k, v in parameters.items() if v is not None))
