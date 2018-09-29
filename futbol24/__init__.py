"""A library that provides a Python interface to the Futbol24 API"""

__author__ = 'Vladimir Zahradnik'
__email__ = 'vladimir.zahradnik@gmail.com'
__copyright__ = 'Copyright (c) 2016 Vladimir Zahradnik'
__license__ = 'Apache License 2.0'
__version__ = '0.1'
__url__ = 'https://github.com/vladimir-zahradnik/futbol24-python'
# __download_url__ = 'TODO'
__description__ = 'A Python wrapper around the Futbol24.com API'

from .api import Api
from .error import Futbol24Error
from .models import (
    Status,
    Range,
    Country,
    Competition,
    League,
    Team,
    Match,
    Matches
    # Teams,
    # Team,
    # Matches,
    # Leagues,
    # Season,
    # League,
    # Match
)
