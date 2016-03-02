# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import)

import json
import requests

from featureswitches.featurecache import FeatureCache
from featureswitches.feature import Feature
from featureswitches.http import HttpClient
from featureswitches.errors import FeatureSwitchesAuthFailed

class FeatureSwitches(object):
    def __init__(self, customer_key, environment_key, default_disable=True, api='https://api.featureswitches.com/v1/'):
        self._customer_key = customer_key
        self._environment_key = environment_key

        self._default = True
        if default_disable:
            self._default = False

        self._api = api
        self._authenticated = False
        self._features = FeatureCache()
        self._http = HttpClient(self)

    def authenticate(self):
        endpoint = 'authenticate'

        if not self._authenticated:
            r = self._http.get(endpoint)

            if r:
                self._authenticated = True
                self.sync()
                return True
                
        raise FeatureSwitchesAuthFailed()

    def sync(self):
        """Pull down a full copy of the environment's features config"""
        if not self._authenticated:
            # Return a not authenticated error
            return False

        endpoint = 'features'
        r = self._http.get(endpoint)
        if r:
            for feature in r.get('features'):
                feature_key = feature.get('feature_key', None)

                f = Feature(
                        key=feature_key,
                        enabled=feature.get('enabled', self._default),
                        include_users=feature.get('include_users', []),
                        exclude_users=feature.get('exclude_users', [])
                )

                print("Setting feature {}".format(feature_key))
                self._features.set_feature(feature_key, f)

    def add_user(self, user_identifier, customer_identifier=None, name=None, email=None):
        """Add the user to FeatureSwitches"""
        if not self._authenticated:
            # Return a not authenticated error
            return False

    def is_enabled(self, feature_key, user_identifier=None):
        if not self._authenticated:
            # Return a not authenticated error
            return False

        feature = self._features.get_feature(feature_key)

        if feature:
            return feature.enabled
        else:
            feature = self._get_feature(feature_key)

            if feature:
                return feature.enabled

        #TODO: This should probably return an exception that the feature wasn't found
        return self._default

    def _get_feature(self, feature_key):
        endpoint = 'feature/enabled'
        payload = {'feature_key': feature_key}

        r = self._http.get(endpoint, params=payload)
        if r:
            feature = Feature(
                    key=feature_key,
                    enabled=r.get('enabled', self._default),
                    include_users=r.get('include_users', []),
                    exclude_users=r.get('exclude_users', [])
            )

            self._features.set_feature(feature_key, feature)

            return feature

        return Feature(
                key=feature_key,
                enabled=self._default
        )

    @property
    def customer_key(self):
        return self._customer_key

    @property
    def environment_key(self):
        return self._environment_key

    @property
    def api(self):
        return self._api

