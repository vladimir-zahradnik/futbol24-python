"""A library that provides a Python interface to the Futbol24 API"""

import json
# static type-checking
from typing import Dict
from urllib.parse import urlparse, urlunparse, urlencode

import requests
import re
from lxml import html

from futbol24.models import Country, Competition, League, Team, Match, Matches
from futbol24.error import Futbol24Error


class Api(object):
    """A python interface into the Futbol24 API"""
    _API_REALM = 'Futbol24 API'

    def __init__(self,
                 input_encoding: str = 'utf-8',
                 request_headers: Dict[str, str] = None,
                 base_url: str = None,
                 user_agent: str = None,
                 add_compat_f24_headers=False,
                 debug_http=False,
                 timeout: int = None,
                 language: str = None):

        self._input_encoding: str = input_encoding
        self._debug_http: bool = debug_http
        self._timeout: int = timeout
        self._language: str = language
        self._cookies: Dict[str, str] = {}

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

    def _initialize_request_headers(self, request_headers: Dict[str, str]):
        if request_headers:
            self._request_headers = request_headers
        else:
            self._request_headers = {}

        self._request_headers['Accept'] = 'application/json'

    def _initialize_user_agent(self, user_agent: str = None):
        if user_agent is None:
            user_agent = 'Futbol24 2.30/61 (compatible)'

        self.set_user_agent(user_agent)

    def _initialize_f24_headers(self, add_compatibility_headers=False):
        """Set the F24 HTTP headers that will be sent to the server.
        They are required to allow authorization on server side.

        """
        if not self._language:
            self._language = 'en'

        self._cookies['f24-asi'] = 'f24-asi=8926cbf3b3a61be64614147d136d389f3b05a64391e2046ae2491ad' \
                                   '152ebd2be2409e754b9aea32dc43e954a008a2fe16d4dee014a9782cc0b542edc6bc55cdd'

        if add_compatibility_headers:
            self._request_headers['F24-App-Version'] = '2.30'
            self._request_headers['F24-Device-Platform'] = 'android'
            self._request_headers['F24-App-Id'] = '1'
            self._request_headers['F24-Device-Language'] = 'slk'
            self._request_headers['F24-Session-Auth'] = self._cookies['f24-asi']

    def set_user_agent(self, user_agent: str):
        """Override the default user agent.
        Args:
          user_agent:
            A string that should be send to the server as the user-agent.
        """
        self._request_headers['User-Agent'] = user_agent

    def get_countries(self) -> [Country]:
        # Build request parameters
        parameters = {}

        url = '%s/v2/countries' % self.base_url
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp, self._input_encoding)

        # Date and time (in unix epoch format) for which data were sent
        # time = data.get('time', 0)

        countries = list(map(Country.new_from_json_dict, data.get('result', {}).get('countries', {}).get('list', [])))

        return countries

    def get_competitions(self) -> [Competition]:
        # Build request parameters
        parameters = {}

        url = '%s/v2/competitions' % self.base_url
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp, self._input_encoding)

        # Date and time (in unix epoch format) for which data were sent
        # time = data.get('time', 0)

        countries = list(map(Country.new_from_json_dict, data.get('result', {}).get('countries', {}).get('list', [])))
        competitions = list(map(lambda competition: self._map_competitions(competition, countries),
                                data.get('result', {}).get('competitions', {}).get('list', [])))

        return competitions

    def get_teams(self) -> [Team]:
        # Build request parameters
        parameters = {}

        url = '%s/v2/teams' % self.base_url
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp, self._input_encoding)

        # Date and time (in unix epoch format) for which data were sent
        # time = data.get('time', 0)

        countries = list(map(Country.new_from_json_dict, data.get('result', {}).get('countries', {}).get('list', [])))
        teams = list(map(lambda team: self._map_teams(team, countries),
                         data.get('result', {}).get('teams', {}).get('list', [])))

        return teams

    # noinspection PyUnresolvedReferences
    def get_team_matches(self, team: Team) -> Matches:
        # Build request parameters
        parameters = {}

        url = '{base_url}/v2/team/{team_id}/matches'.format(base_url=self.base_url, team_id=team.id)
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp, self._input_encoding)

        # Date and time (in unix epoch format) for which data were sent
        # time = data.get('time', 0)

        countries = list(map(Country.new_from_json_dict, data.get('result', {}).get('countries', {}).get('list', [])))

        competitions = list(map(lambda competition: self._map_competitions(competition, countries),
                                data.get('result', {}).get('competitions', {}).get('list', [])))

        leagues = list(map(lambda league: self._map_leagues(league, competitions),
                           data.get('result', {}).get('leagues', {}).get('list', [])))

        teams = list(map(lambda team: self._map_teams(team, countries),
                         data.get('result', {}).get('teams', {}).get('list', [])))

        matches = list(map(lambda match: self._map_matches(match, leagues, teams),
                           data.get('result', {}).get('matches', {}).get('list', [])))

        return Matches(matches)

    # noinspection PyUnresolvedReferences
    def get_team_info(self, team: Team) -> str:
        # Build request parameters
        parameters = {}

        # No API available, we need to scrape the data from the web
        url = '{base_url}/team/{country}/{team_name}/'.format(base_url='https://www.futbol24.com',
                                                              country=self._replace_characters(team.country.name),
                                                              team_name=self._replace_characters(team.name))
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_team_info_http_response(resp, self._input_encoding)

        return data

    def get_daily_matches(self) -> Matches:
        # Build request parameters
        parameters = {}

        url = '%s/v2/matches/day' % self.base_url
        resp = self._request_url(url, 'GET', data=parameters)
        data = self._parse_and_check_http_response(resp, self._input_encoding)

        # Date and time (in unix epoch format) for which data were sent
        # time = data.get('time', 0)

        # Status of last db updates
        # status = Status.new_from_json_dict(data.get('result', {}).get('status', {}))

        # Date range for matches
        # range = Range.new_from_json_dict(data.get('result', {}).get('range', {}))

        countries = list(map(Country.new_from_json_dict, data.get('result', {}).get('countries', {}).get('list', [])))

        competitions = list(map(lambda competition: self._map_competitions(competition, countries),
                                data.get('result', {}).get('competitions', {}).get('list', [])))

        leagues = list(map(lambda league: self._map_leagues(league, competitions),
                           data.get('result', {}).get('leagues', {}).get('list', [])))

        teams = list(map(lambda team: self._map_teams(team, countries),
                         data.get('result', {}).get('teams', {}).get('list', [])))

        matches = list(map(lambda match: self._map_matches(match, leagues, teams),
                           data.get('result', {}).get('matches', {}).get('list', [])))

        return Matches(matches)

    # def get_team_details(self, team_id: int) -> str:
    #     # Build request parameters
    #     parameters = {}
    #
    #     url = '{0}/v2/team/{1}'.format(self.base_url, team_id)
    #     resp = self._request_url(url, 'GET', data=parameters)
    #     data = self._parse_and_check_http_response(resp)
    #
    #     # Parse countries
    #     data.get('countries', {})
    #
    #     # data = self._parse_and_check_http_response(resp)
    #     return resp.content.decode('utf-8')

    # def get_countries(self, get_only_countries_with_stats_tables=False) -> [Country]:
    #     # Build request parameters
    #     parameters = {}
    #
    #     if get_only_countries_with_stats_tables:
    #         parameters['filter'] = 'tables'
    #
    #     url = '%s/countries' % self.base_url
    #
    #     resp = self._request_url(url, 'GET', data=parameters)
    #     data = self._parse_and_check_http_response(resp)
    #
    #     return [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')]
    #
    # # noinspection PyUnresolvedReferences
    # def get_teams(self, country: Country):
    #     try:
    #         if int(country.country_id) < 0:
    #             raise Futbol24Error({'message': "'country_id' must be a positive number"})
    #     except ValueError or TypeError:
    #         raise Futbol24Error({'message': "'country_id' must be an integer"})
    #
    #     # Build request parameters
    #     parameters = {}
    #
    #     url = '{0}/country/{1}/teams'.format(self.base_url, country.country_id)
    #
    #     resp = self._request_url(url, 'GET', data=parameters)
    #     data = self._parse_and_check_http_response(resp)
    #
    #     teams = {'countries': [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')],
    #              'teams': [Team.new_from_json_dict(x) for x in data.get('teams', {}).get('list', '')]}
    #
    #     return Teams.new_from_json_dict(teams)
    #
    # # noinspection PyUnresolvedReferences
    # def get_leagues(self, country: Country, get_only_leagues_with_stats_tables=False):
    #     try:
    #         if int(country.country_id) < 0:
    #             raise Futbol24Error({'message': "'country_id' must be a positive number"})
    #     except ValueError or TypeError:
    #         raise Futbol24Error({'message': "'country_id' must be an integer"})
    #
    #     # Build request parameters
    #     parameters = {}
    #
    #     if get_only_leagues_with_stats_tables:
    #         parameters['filter'] = 'tables'
    #
    #     url = '{0}/country/{1}/leagues'.format(self.base_url, country.country_id)
    #
    #     resp = self._request_url(url, 'GET', data=parameters)
    #     data = self._parse_and_check_http_response(resp)
    #
    #     leagues = {}
    #
    #     try:
    #         country = data['countries']['list'][0]
    #     except TypeError:
    #         country = None
    #
    #     if country is not None:
    #         leagues['country'] = country
    #
    #     leagues['seasons'] = [Season.new_from_json_dict(x) for x in data.get('seasons', {}).get('list', '')]
    #     leagues['leagues'] = [League.new_from_json_dict(x) for x in data.get('leagues', {}).get('list', '')]
    #
    #     return Leagues.new_from_json_dict(leagues)
    #
    # def get_updated_matches(self, update_id: int = None):
    #     # Build request parameters
    #     parameters = {}
    #
    #     if update_id:
    #         url = '{0}/matches/update/{1}'.format(self.base_url, update_id)
    #     else:
    #         url = '%s/matches/update' % self.base_url
    #
    #     resp = self._request_url(url, 'GET', data=parameters)
    #     data = self._parse_and_check_http_response(resp)
    #
    #     matches = {'countries': [Country.new_from_json_dict(x) for x in data.get('countries', {}).get('list', '')],
    #                'seasons': [Season.new_from_json_dict(x) for x in data.get('seasons', {}).get('list', '')],
    #                'leagues': [League.new_from_json_dict(x) for x in data.get('leagues', {}).get('list', '')],
    #                'matches': [Match.new_from_json_dict(x) for x in data.get('matches', {}).get('list', '')],
    #                'range': data.get('matches', {}).get('range', ''),
    #                'update': data.get('matches', {}).get('update', '')}
    #
    #     return Matches.new_from_json_dict(matches)

    def _request_url(self, url, method, data: Dict[str, str] = None, json_data: str = None) -> requests.Response:
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
            elif json_data:
                self._request_headers['Content-Type'] = 'application/json'
                resp = requests.post(url, headers=self._request_headers, cookies=self._cookies,
                                     json=json_data, timeout=self._timeout)
            else:
                resp = 0  # POST request, but without data or json

        elif method == 'GET':
            url = self._build_url(url, extra_params=data)
            resp = requests.get(url, headers=self._request_headers, cookies=self._cookies, timeout=self._timeout)

        else:
            resp = 0  # if not a POST or GET request

        return resp

    def _build_url(self, url: str, path_elements: [str] = None, extra_params: [str] = None):
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

    @staticmethod
    def _parse_and_check_http_response(response: requests.Response, encoding='utf-8'):
        """ Check http response returned from Futbol24, try to parse it as JSON and return
        an empty dictionary if there is any error.
        """
        if not response.ok:
            raise Futbol24Error({'message': "Error {0} {1}".format(response.status_code, response.reason)})

        json_data = response.content.decode(encoding)
        try:
            data = json.loads(json_data)
        except TypeError or json.JSONDecodeError:
            raise Futbol24Error({'message': "Invalid JSON content"})

        return data

    @staticmethod
    def _encode_parameters(parameters: Dict[str, str]) -> str or None:
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

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _map_competitions(competition: Dict[str, str], countries: [Country]):
        competition: Competition = Competition.new_from_json_dict(competition)
        competition_country = list(filter(lambda country: country.id == competition.country_id, countries))[0]
        delattr(competition, 'country_id')
        setattr(competition, 'country', competition_country)

        return competition

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _map_leagues(league: Dict[str, str], competitions: [Competition]):
        league: League = League.new_from_json_dict(league)
        league_competition = list(filter(lambda competition: competition.id == league.competition_id, competitions))[0]
        delattr(league, 'competition_id')
        setattr(league, 'competition', league_competition)

        return league

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _map_teams(team: Dict[str, str], countries: [Country]):
        team: Team = Team.new_from_json_dict(team)
        team_country = list(filter(lambda country: country.id == team.country_id, countries))[0]
        delattr(team, 'country_id')
        setattr(team, 'country', team_country)

        return team

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _map_matches(match: Dict[str, str], leagues: [League], teams: [Team]):
        match: Match = Match.new_from_json_dict(match)
        match_league = list(filter(lambda league: league.id == match.league_id, leagues))[0]
        delattr(match, 'league_id')
        setattr(match, 'league', match_league)

        home_team = list(filter(lambda team: team.id == match.home.get('team_id', -1), teams))[0]
        del match.home['team_id']
        match.home['team'] = home_team

        guest_team = list(filter(lambda team: team.id == match.guest.get('team_id', -1), teams))[0]
        del match.guest['team_id']
        match.guest['team'] = guest_team

        return match

    @staticmethod
    def _parse_team_info_http_response(response: requests.Response, encoding='utf-8') -> Dict[str, tuple]:
        """ Parse team info http response returned from Futbol24. It is returned as html which
        needs to be parsed.
        """
        if not response.ok:
            raise Futbol24Error({'message': "Error {0} {1}".format(response.status_code, response.reason)})

        html_data = response.content.decode(encoding)
        goal_stats_html = re.search(r'Goals in minutes.+(?P<table><table.+</table>)',
                              html_data, flags=re.DOTALL | re.MULTILINE)

        goals_in_minutes = {}

        if goal_stats_html:
            goal_table=html.fromstring(goal_stats_html.group('table'))
            goal_table_rows=goal_table.xpath('.//tr')

            for row in goal_table_rows:
                min_range=row.xpath('./td[contains(@class, "under")]/text()')
                percent = row.xpath('./td[contains(@class, "percent")]/text()')
                goals = row.xpath('./td[contains(@class, "bold")]/text()')

                goals_in_minutes[str(min_range[0])]=(str(percent[0]), int(goals[0]))

        return goals_in_minutes

    @staticmethod
    def _replace_characters(text: str) -> str:
        translation_table = {
            ' ' : '-',
            '/': '-',
            '\\': '-',
            '–': '-',
            '(' : '',
            ')': '',
            '.': '',
            '\'': '',
            'º': '',
            '°': '',
            '‘': '',
            '’': '',
            '&': '',
            'á': 'a',
            'à': 'a',
            'ä': 'a',
            'â': 'a',
            'ã': 'a',
            'å': 'a',
            'ă': 'a',
            'ą': 'a',
            'Å': 'A',
            'Á': 'A',
            'Ä': 'A',
            'æ': 'ae',
            'ć': 'c',
            'č': 'c',
            'ç': 'c',
            'Ç': 'C',
            'Č': 'C',
            'đ': 'd',
            'ď': 'd',
            'ð': 'd',
            'Ď': 'D',
            'ë': 'e',
            'è': 'e',
            'é': 'e',
            'ê': 'e',
            'ě': 'e',
            'ė': 'e',
            'ę': 'e',
            'ə': '',
            'É': 'e',
            'ğ': 'g',
            'ħ': 'h',
            'í': 'i',
            'Í': 'I',
            'ī': 'i',
            'ı': 'i',
            'î': 'i',
            'ï': 'i',
            'ì': 'i',
            'İ': 'I',
            'Î': 'I',
            'ĺ': 'l',
            'ľ': 'l',
            'ł': 'l',
            'Ł': 'L',
            'ň': 'n',
            'ń': 'n',
            'ñ': 'n',
            'ņ': 'n',
            'Ñ': 'N',
            'ø': 'o',
            'ö': 'o',
            'Ö': 'O',
            'ó': 'o',
            'õ': 'o',
            'ô': 'o',
            'ő': 'o',
            'Ø': 'O',
            'Ó': 'O',
            'œ': 'oe',
            'ŕ': 'r',
            'ř': 'r',
            'Ř': 'R',
            'ś': 's',
            'š': 's',
            'ş': 's',
            'ș': 's',
            'Ș': 'S',
            'Ş': 'S',
            'Ś': 'S',
            'Š': 'S',
            'ß': 'ss',
            'ť': 't',
            'ţ': 't',
            'ț': 't',
            'ü': 'u',
            'ú': 'u',
            'ů': 'u',
            'Ü': 'U',
            'ū': 'u',
            'Ú': 'U',
            'ų': 'u',
            'ý': 'y',
            'ž': 'z',
            'ż': 'z',
            'ź': 'z',
            'Ž': 'Z',
            'Ż': 'Z'

        }

        for char, repl in translation_table.items():
            text = text.replace(char, repl)

        return text
