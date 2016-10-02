"""A library that provides a Python interface to the Futbol24 API"""

import json
from urllib.parse import urlparse, urlunparse, urlencode

import requests

from futbol24 import Country, Teams, Team, Matches, Season, League, Match, Leagues
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
                 timeout=None,
                 language=None):

        self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
        self._debug_http = debug_http
        self._timeout = timeout
        self._language = language
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
        if not self._language:
            self._language = 'en'

        self._cookies['F24-CC'] = self._language
        self._cookies['f24'] = '5-038b0e6af9e7390bdfd37bd1c85e6790265c7940'

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

    def get_countries(self, get_only_countries_with_stats_tables=False):
        # Build request parameters
        parameters = {}

        if get_only_countries_with_stats_tables:
            parameters['filter'] = 'tables'

        url = '%s/countries' % self.base_url

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp)

        return [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')]

    def get_teams(self, country):
        try:
            if int(country.id) < 0:
                raise Futbol24Error({'message': "'country_id' must be a positive number"})
        except ValueError or TypeError:
            raise Futbol24Error({'message': "'country_id' must be an integer"})

        # Build request parameters
        parameters = {}

        url = '{0}/country/{1}/teams'.format(self.base_url, country.id)

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp)

        teams = {'countries': [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')],
                 'teams': [Team.new_from_json_dict(x) for x in data.get('teams', {}).get('list', '')]}

        return Teams.new_from_json_dict(teams)

    def get_leagues(self, country, get_only_leagues_with_stats_tables=False):
        try:
            if int(country.id) < 0:
                raise Futbol24Error({'message': "'country_id' must be a positive number"})
        except ValueError or TypeError:
            raise Futbol24Error({'message': "'country_id' must be an integer"})

        # Build request parameters
        parameters = {}

        if get_only_leagues_with_stats_tables:
            parameters['filter'] = 'tables'

        url = '{0}/country/{1}/leagues'.format(self.base_url, country.id)

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp)

        leagues = {}

        try:
            country = data['countries']['list'][0]
        except:
            country = None

        if country is not None:
            leagues['country'] = country

        leagues['seasons'] = [Season.new_from_json_dict(x) for x in data.get('seasons', {}).get('list', '')]
        leagues['leagues'] = [League.new_from_json_dict(x) for x in data.get('leagues', {}).get('list', '')]

        return Leagues.new_from_json_dict(leagues)

    def get_updated_matches(self, update_id=None):
        # Build request parameters
        parameters = {}

        if update_id:
            url = '{0}/matches/update/{1}'.format(self.base_url, update_id)
        else:
            url = '%s/matches/update' % self.base_url

        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp)

        matches = {'countries': [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')],
                   'seasons': [Season.new_from_json_dict(x) for x in data.get('seasons', {}).get('list', '')],
                   'leagues': [League.new_from_json_dict(x) for x in data.get('leagues', {}).get('list', '')],
                   'matches': [Match.new_from_json_dict(x) for x in data.get('matches', {}).get('list', '')],
                   'range': data.get('matches', {}).get('range', ''),
                   'update': data.get('matches', {}).get('update', '')}

        return Matches.new_from_json_dict(matches)


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

    def _parse_and_check_http_response(self, response):
        """ Check http response returned from Futbol24, try to parse it as JSON and return
        an empty dictionary if there is any error.
        """
        if not response.ok:
            raise Futbol24Error({'message': "Error {0} {1}".format(response.status_code, response.reason)})

        json_data = response.content.decode('utf-8')
        try:
            data = json.loads(json_data)

        except:
            raise Futbol24Error({'message': "Invalid JSON content"})

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
