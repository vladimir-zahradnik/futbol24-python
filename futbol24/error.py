#!/usr/bin/env python


class Futbol24Error(Exception):
    """Base class for Futbol24 errors"""

    @property
    def message(self):
        """Returns the first argument used to construct this error."""
        return self.args[0]
