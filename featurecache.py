# -*- coding: utf-8 -*-

import time

from feature import Feature

class FeatureCache(dict):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = dict.__new__(cls)
            cls._cache_expiration = kwargs['cache_expiration']
        return cls._instance

    @classmethod
    def getInstance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = ditc.__new__(cls)
        return cls._instance

    def get_feature(self, key):
        feature = self.get(key, None)

        if feature is not None:
            if time.time() - feature.created >= self._cache_expiration:
                del self[key]
                return None
        return feature

    def set_feature(self, key, feature):
        self[key] = feature

    def get_keys(self):
        result = []

        for key, value in self.iteritems():
            result.append({'feature_key': key, 'created': value.created})

        return result
