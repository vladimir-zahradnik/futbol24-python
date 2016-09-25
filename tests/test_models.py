import json
import unittest

import futbol24


class ModelsTest(unittest.TestCase):
    with open('../testdata/models/models_country.json', 'rb') as f:
        COUNTRY_SAMPLE_JSON = json.loads(f.read().decode('utf8'))

    def test_country(self):
        """ Test futbol24.Country object """
        country = futbol24.Country.new_from_json_dict(self.COUNTRY_SAMPLE_JSON)
        try:
            country.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(country.as_json_string())
        self.assertTrue(country.as_dict())
