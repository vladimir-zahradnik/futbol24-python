import json

# static type-checking
from typing import Dict

try:
    from rfc822 import parsedate
except ImportError:
    from email.utils import parsedate


class BaseModel(object):
    """ Base class from which all Futbol24 models will inherit. """

    def __init__(self, **kwargs):
        self.param_defaults = {}

    def __str__(self) -> str:
        """ Returns a string representation of model. By default
        this is the same as AsJsonString(). """
        return self.as_json_string()

    def __eq__(self, other) -> bool:
        return other and self.as_dict() == other.as_dict()

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def as_json_string(self) -> str:
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


# noinspection PyUnresolvedReferences
class Status(BaseModel):
    """ A class representing status structure. Each field contains
     timestamp (unix epoch time) of database update for corresponding type. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults: Dict[str, int] = {
            'update_countries': None,
            'update_competitions': None,
            'update_seasons': None,
            'update_leagues': None,
            'update_teams': None,
            'update_matches': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Status(update_keys)"


# noinspection PyUnresolvedReferences
class Range(BaseModel):
    """ A class representing country structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'date_d': None,  # str
            'date_m': None,  # str
            'type': None,  # int
            'hour_new_day': None,  # int
            'hour': None,  # int
            'day': None,  # int, unix epoch time
            'day_s': None,  # str, day as a string
            'start': None,  # int, unix epoch time
            'start_s': None,  # str, start date and time as a string
            'end': None,  # int, unix epoch time
            'end_s': None  # str, end date and time as a string
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Range({start_str} - {end_str})".format(
            start_str=self.start_s,
            end_str=self.end_s)


# noinspection PyUnresolvedReferences
class Country(BaseModel):
    """ A class representing country structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'national': False,
            'name': None,
            'sname': None,
            'flag_url_medium': None,
            'updated': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Country(ID={country_id}, Name={name!r}, Short Name={short_name})".format(
            country_id=self.id,
            national=self.national,
            name=self.name,
            short_name=self.sname)


# noinspection PyUnresolvedReferences
class Competition(BaseModel):
    """ A class representing competiton structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'country_id': None,
            'popularity': None,
            'name': None,
            'foreground': None,
            'background': None,
            'standings': False,
            'available_standings': False,
            'updated': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Competition(ID={competition_id}, Name={name!r})".format(
            competition_id=self.id,
            name=self.name)


# noinspection PyUnresolvedReferences
class League(BaseModel):
    """ A class representing league structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'competition_id': None,
            'season_id': None,
            'name': None,
            'dname': None,
            'foreground': None,
            'background': False,
            'standings': False,
            'available_standings': None,
            'updated': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "League(ID={league_id}, Name={name!r})".format(
            league_id=self.id,
            name=self.name)


# noinspection PyUnresolvedReferences
class Team(BaseModel):
    """ A class representing team structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'country_id': None,
            'name': None,
            'sname': None,
            'updated': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Team(ID={team_id}, Name={name!r})".format(
            team_id=self.id,
            name=self.name)


# noinspection PyUnresolvedReferences
class Match(BaseModel):
    """ A class representing match structure. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_defaults = {
            'id': None,
            'league_id': None,
            'start_date': None,
            'end_date': None,
            'start_offset': None,
            'half_length': None,
            'half_offset': None,
            'status_id': None,
            'minutes': None,
            'playnow': None,
            'injury': None,
            'home': None,
            'guest': None,
            'available_mask': None,
            'updated_actions': None,
            'updated_events_play': None,
            'updated': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self) -> str:
        return "Match(ID={match_id})".format(
            match_id=self.id)


# # noinspection PyUnresolvedReferences
# class Teams(BaseModel):
#     """ A class representing teams structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'countries': [],
#             'teams': []
#         }
#
#         for (param, default) in self.param_defaults.items():
#             setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Teams(Country={country_name}, Count={number_of_teams})".format(
#             country_name=self.countries.get(0, "Unknown"),
#             number_of_teams=len(self.teams))
#
#
# # noinspection PyUnresolvedReferences
# class Team(BaseModel):
#     """ A class representing team structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'team_id': None,
#             'country_id': None,
#             'flag': None,
#             'name': None,
#             'update': None
#         }
#
#         for (param, default) in self.param_defaults.items():
#             if param == 'country_id':
#                 country = kwargs.get('country')
#                 if country:
#                     team_id = country['country_id']
#                     setattr(self, param, team_id)
#             else:
#                 setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Team(ID={team_id}, Name={name!r})".format(
#             team_id=self.team_id,
#             name=self.name)
#
#
# # noinspection PyUnresolvedReferences
# class Matches(BaseModel):
#     """ A class representing matches structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'countries': [],
#             'seasons': [],
#             'leagues': [],
#             'matches': [],
#             'range': {},
#             'update': None
#         }
#
#         for (param, default) in self.param_defaults.items():
#             setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Matches(Count={number_of_matches}, Countries={number_of_countries}," \
#                " Leagues={number_of_leagues})".format(
#                 number_of_matches=len(self.matches),
#                 number_of_countries=len(self.countries),
#                 number_of_leagues=len(self.leagues))
#
#
# # noinspection PyUnresolvedReferences
# class Leagues(BaseModel):
#     """ A class representing leagues structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'country': None,
#             'seasons': [],
#             'leagues': []
#         }
#
#         for (param, default) in self.param_defaults.items():
#             setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Country={country_name}, Leagues(Count={number_of_leagues})".format(
#             country_name=self.country.name,
#             number_of_leagues=len(self.leagues))
#
#
# # noinspection PyUnresolvedReferences
# class Season(BaseModel):
#     """ A class representing season structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'season_id': None,
#             'name': None,
#             'sname': None,
#             'update': None
#         }
#
#         for (param, default) in self.param_defaults.items():
#             setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Season(ID={season_id}, Name={name!r}, Short Name={short_name})".format(
#             season_id=self.season_id,
#             name=self.name,
#             short_name=self.sname)
#
#
# # noinspection PyUnresolvedReferences
# class League(BaseModel):
#     """ A class representing league structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'league_id': None,
#             'pid': None,
#             'country_id': None,
#             'season_id': None,
#             'order': None,
#             'has_tables': False,
#             'name': None,
#             'sname': None,
#             'colors': {},
#             'update': None
#         }
#
#         for (param, default) in self.param_defaults.items():
#             if param == 'country_id':
#                 country = kwargs.get('country')
#                 if country:
#                     league_id = country['country_id']
#                     setattr(self, param, league_id)
#
#             elif param == 'season_id':
#                 season = kwargs.get('season')
#                 if season:
#                     league_id = season['season_id']
#                     setattr(self, param, league_id)
#
#             elif param == 'has_tables':
#                 setattr(self, param, kwargs.get('tables', False))
#             else:
#                 setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "League(ID={league_id}, Name={name!r}, Short Name={short_name}, Has Tables={has_tables})".format(
#             league_id=self.league_id,
#             name=self.name,
#             short_name=self.sname,
#             has_tables=self.has_tables)
#
#
# # noinspection PyUnresolvedReferences
# class Match(BaseModel):
#     """ A class representing match structure. """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.param_defaults = {
#             'match_id': None,
#             'league_id': None,
#             'start_date': None,
#             'status': None,
#             'played': [],
#             'teams': {},
#             'update': {}
#         }
#
#         for (param, default) in self.param_defaults.items():
#             if param == 'league_id':
#                 league = kwargs.get('league')
#                 if league:
#                     match_id = league['league_id']
#                     setattr(self, param, match_id)
#
#             elif param == 'start_date':
#                 date = kwargs.get('date')
#                 if date:
#                     start_date = date['start']
#                     setattr(self, param, start_date)
#
#             elif param == 'teams':
#                 data = {'home': {'team': Team.new_from_json_dict(kwargs.get('teams')['home']['team']),
#                                  'scores': kwargs.get('teams')['home']['scores'],
#                                  'cards': kwargs.get('teams')['home']['cards']},
#                         'guest': {'team': Team.new_from_json_dict(kwargs.get('teams')['guest']['team']),
#                                   'scores': kwargs.get('teams')['guest']['scores'],
#                                   'cards': kwargs.get('teams')['guest']['cards']}}
#
#                 setattr(self, param, data)
#             else:
#                 setattr(self, param, kwargs.get(param, default))
#
#     def __repr__(self) -> str:
#         return "Match(ID={match_id}, Home Team={home_team}, Guest Team={guest_team})".format(
#             match_id=self.match_id,
#             home_team=self.teams['home']['team'].name,
#             guest_team=self.teams['guest']['team'].name)
