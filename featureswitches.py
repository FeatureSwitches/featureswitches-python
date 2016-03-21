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
    API = 'https://api.featureswitches.com/v1/'
    VERSION = '0.8.0'

    def __init__(self, customer_key, environment_key, cache_timeout=300, check_interval=10, api=None):
        self._customer_key = customer_key
        self._environment_key = environment_key

        self._api = api if api else API
        self._authenticated = False
        self._last_feature_update = 0
        self._last_dirty_check = 0
        self._last_check = 0
        self._http = HttpClient(self)

        self._cache_timeout = cache_timeout
        self._check_interval = check_interval

        FeatureCache()

        self.sync()

        #t = threading.Thread(target=self._dirty_check)
        #t.setDaemon(True)
        #t.start()

    def authenticate(self):
        endpoint = 'authenticate'
        if self._http.get(endpoint):
            return True
                
        raise FeatureSwitchesAuthFailed()

    def sync(self):
        endpoint = 'features'
        if self._current_timestamp() < (self._last_check - self._check_interval):
            r = self._http.get(endpoint)
            if r:
                print("LAST FEATURE UPDATE: {}".format(r.get('last_update')))

                self._last_feature_update = r.get('last_update')
                self._last_check = self._current_timestamp()

                feature_cache = FeatureCache.getInstance()

                for feature in r.get('features'):
                    feature_key = feature.get('feature_key', None)

                    f = Feature(
                            key=feature_key,
                            enabled=feature.get('enabled'),
                            include_users=feature.get('include_users', []),
                            exclude_users=feature.get('exclude_users', [])
                    )

                    feature_cache.set_feature(feature_key, f)


    def add_user(self, user_identifier, customer_identifier=None, name=None, email=None):
        endpoint = 'user/add'
        payload = {
            'user_identifier': user_identifier,
            'customer_identifier': customer_identifier,
            'name': name,
            'email': email,
        }

        r = self._http.post(endpoint, payload)

        if r and r.get('success'):
            return True
        return False


    def is_enabled(self, feature_key, user_identifier=None, default=False):
        feature_cache = FeatureCache.getInstance()
        feature = feature_cache.get_feature(feature_key)

        if feature and not self._cache_is_stale(feature) and feature.enabled:
            if feature.include_users:
                if user_identifier in feature.include_users:
                    return True
                else:
                    return False

            if feature.exclude_users:
                if user_identifier in feature.exclude_users:
                    return False

            if not user_identifier and (feature.include_users or feature.exclude_users):
                return False

            return feature.enabled
        elif feature and not feature.enabled:
            return False
        else:
            feature = self._get_feature(feature_key, user_identifier)

            if feature:
                return self.is_enabled(feature_key, user_identifier)

        return default

    def _cache_is_stale(self, feature):
        cache_expiration = self._current_timestamp() - self._cache_timeout

        print("Created: {}, Cache Expiration: {}, Last Dirty Check: {}".format(feature.created, cache_expiration, self._last_dirty_check))
        if feature.created > cache_expiration and self._last_dirty_check > cache_expiration:
            return False

        if self._last_dirty_check < cache_expiration:
            return True

        return False

    def _get_feature(self, feature_key, user_identifier=None):
        endpoint = 'feature/enabled'
        payload = {'feature_key': feature_key}

        if user_identifier:
            payload['user_identifier'] = user_identifier

        r = self._http.get(endpoint, params=payload)
        if r:
            feature = Feature(
                    key=feature_key,
                    enabled=r.get('enabled'),
                    include_users=r.get('include_users', []),
                    exclude_users=r.get('exclude_users', []),
            )

            feature_cache = FeatureCache.getInstance()
            feature_cache.set_feature(feature_key, feature)

            return feature

        return False

    def _dirty_check(self):
        endpoint = 'dirty-check'
        while True:
            r = self._http.get(endpoint)
            print("Last Updated {}, Local Last Updated {}".format(r.get('last_update'), self._last_feature_update))
            if r and r.get('last_update') > self._last_feature_update:
                print("Feature Update, Syncing...")
                self.sync()
            self._last_dirty_check = self._current_timestamp()
            time.sleep(self._check_interval)


    def _current_timestamp(self):
        return int(time.time())

    @property
    def customer_key(self):
        return self._customer_key

    @property
    def environment_key(self):
        return self._environment_key

    @property
    def api(self):
        return self._api

