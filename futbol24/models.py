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
    """A class representing the suggested user category structure. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'id': None,
            'name': None,
            'order': None,
            'sname': None,
            'teams': None,
            'type': None,
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
