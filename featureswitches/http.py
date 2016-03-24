# -*- coding: utf-8 -*-

import requests


class HttpClient(object):

    def __init__(self, featureswitches):
        self._fs = featureswitches

    def _auth_headers(self):
        return {'Authorization': '{customer_key}:{environment_key}'.format(
            customer_key=self._fs.customer_key,
            environment_key=self._fs.environment_key
        )}

    def get(self, endpoint, params=None):
        try:
            r = requests.get(self._fs.api + endpoint, headers=self._auth_headers(), params=params)

            if r.status_code == 200:
                return r.json()
        except requests.RequestException as e:
            pass
        return False

    def post(self, endpoint, payload=None):
        try:
            r = requests.post(self._fs.api + endpoint, headers=self._auth_headers(), data=payload)

            if r.status_code == 200:
                return r.json()
        except requests.RequestException as e:
            pass
        return False

