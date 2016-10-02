import json
from calendar import timegm

try:
    from rfc822 import parsedate
except ImportError:
    from email.utils import parsedate


class BaseModel(object):
    """ Base class from which all Futbol24 models will inherit. """

    def __init__(self, **kwargs):
        self.param_defaults = {}

    def __str__(self):
        """ Returns a string representation of model. By default
        this is the same as AsJsonString(). """
        return self.as_json_string()

    def __eq__(self, other):
        return other and self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def as_json_string(self):
        """ Returns the model as a JSON string based on key/value
        pairs returned from the as_dict() method. """
        return json.dumps(self.as_dict(), sort_keys=True)

    def as_dict(self):
        """ Create a dictionary representation of the object."""
        data = {}

        for (key, value) in self.param_defaults.items():

            # If the value is a list, we need to create a list to hold the
            # dicts created by an object supporting the as_dict() method,
            # i.e., if it inherits from BaseModel. If the item in the list
            # doesn't support the as_dict() method, then we assign the value
            # directly.
            if isinstance(getattr(self, key, None), (list, tuple, set)):
                data[key] = list()
                for subobj in getattr(self, key, None):
                    if getattr(subobj, 'as_dict', None):
                        data[key].append(subobj.as_dict())
                    else:
                        data[key].append(subobj)

            # Not a list, *but still a subclass of BaseModel* and
            # we can assign the data[key] directly with the as_dict()
            # method of the object.
            elif getattr(getattr(self, key, None), 'as_dict', None):
                data[key] = getattr(self, key).as_dict()

            # If the value doesn't have an as_dict() method, i.e., it's not
            # something that subclasses BaseModel, then we can use direct
            # assignment.
            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)
        return data

    @classmethod
    def new_from_json_dict(cls, data, **kwargs):
        """ Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.
        Args:
            data: A JSON dict, as converted from the JSON in the twitter API.
        """

        if kwargs:
            for key, val in kwargs.items():
                data[key] = val

        return cls(**data)


class Country(BaseModel):
    """ A class representing country structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'type': None,
            'name': None,
            'sname': None,
            'order': None,
            'tables': None,
            'teams': None,
            'update': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Country(ID={country_id}, Name={name!r}, Short Name={short_name}, Teams={number_of_teams})".format(
            country_id=self.id,
            name=self.name,
            short_name=self.sname,
            number_of_teams=self.teams)

class Teams(BaseModel):
    """ A class representing teams structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'countries': [],
            'teams': []
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Teams(Country={country_name}, Count={number_of_teams})".format(
            country_name=self.countries.get(0, "Unknown"),
            number_of_teams=len(self.teams))

class Team(BaseModel):
    """ A class representing team structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'country_id': None,
            'flag': None,
            'name': None,
            'update': None
        }

        for (param, default) in self.param_defaults.items():
            if param == 'country_id':
                country = kwargs.get('country')
                if country:
                    id = country['id']
                    setattr(self, param, id)
            else:
                setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Team(ID={team_id}, Name={name!r})".format(
            team_id=self.id,
            name=self.name)

class Matches(BaseModel):
    """ A class representing matches structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'countries': [],
            'seasons': [],
            'leagues': [],
            'matches': [],
            'range': {},
            'update': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Matches(Count={number_of_matches}, Countries={number_of_countries}, Leagues={number_of_leagues})".format(
            number_of_matches=len(self.matches),
            number_of_countries=len(self.countries),
            number_of_leagues=len(self.leagues))

class Leagues(BaseModel):
    """ A class representing leagues structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'country': None,
            'seasons': [],
            'leagues': []
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Country={country_name}, Leagues(Count={number_of_leagues})".format(
            country_name=self.country.name,
            number_of_leagues=len(self.leagues))


class Season(BaseModel):
    """ A class representing season structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'name': None,
            'sname': None,
            'update': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Season(ID={season_id}, Name={name!r}, Short Name={short_name})".format(
            season_id=self.id,
            name=self.name,
            short_name=self.sname)

class League(BaseModel):
    """ A class representing league structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'pid': None,
            'country_id': None,
            'season_id': None,
            'order': None,
            'has_tables': False,
            'name': None,
            'sname': None,
            'colors': {},
            'update': None
        }

        for (param, default) in self.param_defaults.items():
            if param == 'country_id':
                country = kwargs.get('country')
                if country:
                    id = country['id']
                    setattr(self, param, id)

            elif param == 'season_id':
                season = kwargs.get('season')
                if season:
                    id = season['id']
                    setattr(self, param, id)

            elif param == 'has_tables':
                setattr(self, param, kwargs.get('tables', False))
            else:
                setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "League(ID={league_id}, Name={name!r}, Short Name={short_name}, Has Tables={has_tables})".format(
            league_id=self.id,
            name=self.name,
            short_name=self.sname,
            has_tables=self.has_tables)

class Match(BaseModel):
    """ A class representing match structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'league_id': None,
            'start_date': None,
            'status': None,
            'played': [],
            'teams': {},
            'update': {}
        }

        for (param, default) in self.param_defaults.items():
            if param == 'league_id':
                league = kwargs.get('league')
                if league:
                    id = league['id']
                    setattr(self, param, id)

            elif param == 'start_date':
                date = kwargs.get('date')
                if date:
                    start_date = date['start']
                    setattr(self, param, start_date)

            elif param == 'teams':
                data = {}
                data['home'] = {'team': Team.new_from_json_dict(kwargs.get('teams')['home']['team']),
                        'scores': kwargs.get('teams')['home']['scores'],
                        'cards': kwargs.get('teams')['home']['cards']}
                data['guest'] = {'team': Team.new_from_json_dict(kwargs.get('teams')['guest']['team']),
                        'scores': kwargs.get('teams')['guest']['scores'],
                        'cards': kwargs.get('teams')['guest']['cards']}

                setattr(self, param, data)
            else:
                setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Match(ID={match_id}, Home Team={home_team}, Guest Team={guest_team})".format(
            match_id=self.id,
            home_team=self.teams['home']['team'].name,
            guest_team=self.teams['guest']['team'].name)
