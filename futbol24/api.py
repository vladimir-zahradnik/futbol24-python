import requests

class Api(object):
    def __init__(self):
        self.base_url = 'http://api.futbol24.gluak.com'

    def get_countries(self):
        url = '%s/countries' % self.base_url

        headers = {'user-agent': 'Futbol24 1.9.1/26 (compatible)'}
        cookies = {'F24-CC':'sk'}
        return requests.get(url, headers=headers, cookies = cookies)

