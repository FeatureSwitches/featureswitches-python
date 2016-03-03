# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import)

import json
import time
import requests
import threading

from featureswitches.featurecache import FeatureCache
from featureswitches.feature import Feature
from featureswitches.http import HttpClient
from featureswitches.errors import FeatureSwitchesAuthFailed

class FeatureSwitches(object):
    def __init__(self, customer_key, environment_key, default_disable=True, cache_expiration=300, api='https://api.featureswitches.com/v1/'):
        self._customer_key = customer_key
        self._environment_key = environment_key

        self._default = True
        if default_disable:
            self._default = False

        self._api = api
        self._authenticated = False
        self._last_feature_update = 0
        self._http = HttpClient(self)

        FeatureCache(cache_expiration=cache_expiration)
        #self._features = FeatureCache.getInstance()

    def authenticate(self):
        endpoint = 'authenticate'

        if not self._authenticated:
            r = self._http.get(endpoint)

            if r:
                self._authenticated = True
                self.sync()

                t = threading.Thread(target=self._dirty_check)
                t.setDaemon(True)
                t.start()

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
            self._last_feature_update = r.get('last_update')
            feature_cache = FeatureCache.getInstance()
            for feature in r.get('features'):
                feature_key = feature.get('feature_key', None)

                f = Feature(
                        key=feature_key,
                        enabled=feature.get('enabled', self._default),
                        include_users=feature.get('include_users', []),
                        exclude_users=feature.get('exclude_users', [])
                )

                #self._features.set_feature(feature_key, f)
                feature_cache.set_feature(feature_key, f)


    def add_user(self, user_identifier, customer_identifier=None, name=None, email=None):
        """Add the user to FeatureSwitches"""
        if not self._authenticated:
            # Return a not authenticated error
            return False

    def is_enabled(self, feature_key, user_identifier=None):
        if not self._authenticated:
            # Return a not authenticated error
            return False

        #feature = self._features.get_feature(feature_key)
        feature_cache = FeatureCache.getInstance()
        feature = feature_cache.get_feature(feature_key)

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

            feature_cache = FeatureCache.getInstance()
            feature_cache.set_feature(feature_key, feature)
            #self._features.set_feature(feature_key, feature)

            return feature

        return Feature(
                key=feature_key,
                enabled=self._default
        )

    def _dirty_check(self):
        endpoint = 'dirty-check'
        while True:
            r = self._http.get(endpoint)
            print("Last Updated {}, Local Last Updated {}".format(r.get('last_update'), self._last_feature_update))
            if r and r.get('last_update') > self._last_feature_update:
                print("Feature Update, Syncing...")
                self.sync()
            time.sleep(10)


    @property
    def customer_key(self):
        return self._customer_key

    @property
    def environment_key(self):
        return self._environment_key

    @property
    def api(self):
        return self._api

