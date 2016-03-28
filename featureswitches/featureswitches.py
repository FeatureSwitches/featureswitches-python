# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import)

import json
import time
import requests
import threading

from featureswitches.feature import Feature
from featureswitches.http import HttpClient
from featureswitches.errors import FeatureSwitchesAuthFailed
from featureswitches.cache_factory import cache_factory
from featureswitches.version import VERSION

class FeatureSwitches(object):
    API = 'https://api.featureswitches.com/v1/'

    def __init__(self, customer_key, environment_key, cache_timeout=300, check_interval=10, api=None):
        self._customer_key = customer_key
        self._environment_key = environment_key

        self._api = api if api else self.API
        self._authenticated = False
        self._last_feature_update = 0
        self._last_dirty_check = 0
        self._last_sync = 0
        self._http = HttpClient(self)

        self._cache_timeout = cache_timeout
        self._check_interval = check_interval

        self._cache = cache_factory()

        if self._cache_timeout > 0:
            self.sync()

            t = threading.Thread(target=self._dirty_check)
            t.setDaemon(True)
            t.start()

    def authenticate(self):
        endpoint = 'authenticate'
        if self._http.get(endpoint):
            return True
                
        raise FeatureSwitchesAuthFailed()

    def sync(self, force=False):
        endpoint = 'features'
        if self._cache_timeout > 0:
            r = self._http.get(endpoint)
            if r:
                self._last_feature_update = r.get('last_update')
                self._last_sync = self._current_timestamp()

                for feature in r.get('features'):
                    feature_key = feature.get('feature_key', None)

                    f = Feature(
                            key=feature_key,
                            enabled=feature.get('enabled'),
                            include_users=feature.get('include_users', []),
                            exclude_users=feature.get('exclude_users', []),
                            last_sync=self._last_sync
                    )

                    self._cache.set(feature_key, f)


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
        try:
            feature = self._cache.get(feature_key, ignore_expiration=True)
        except ValueError:
            feature = None

        if feature and not self._cache_is_stale(feature):
            return self._enabled_for_user(feature, user_identifier)
        else:
            feature = self._get_feature(feature_key, user_identifier)

            if feature:
                return self._enabled_for_user(feature, user_identifier)

        return default

    def _enabled_for_user(self, feature, user_identifier):
        if feature.enabled:
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
        return feature.enabled

    def _cache_is_stale(self, feature):
        if self._cache_timeout == 0:
            return True

        cache_expiration = self._current_timestamp() - self._cache_timeout

        if feature.last_sync > cache_expiration and self._last_dirty_check > cache_expiration:
            return False
        elif feature.last_sync < cache_expiration and self._last_dirty_check == 0:
            return True

        if self._last_dirty_check != 0 and self._last_dirty_check < cache_expiration:
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
                    last_sync=self._current_timestamp()
            )

            if self._cache_timeout > 0:
                self._cache.set(feature_key, feature)

            return feature

        return False

    def _dirty_check(self):
        endpoint = 'dirty-check'
        while True:
            r = self._http.get(endpoint)
            if r and r.get('last_update') > self._last_feature_update:
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

