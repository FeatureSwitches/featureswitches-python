# -*- coding: utf-8 -*-

class Feature(object):

    def __init__(self, key, enabled, include_users=[], exclude_users=[], last_sync=None):
        self._feature = {
            'key': key,
            'enabled': enabled,
            'include_users': include_users,
            'exclude_users': exclude_users,
            'last_sync': last_sync
        }

    @property
    def key(self):
        return self._feature['key']

    @property
    def enabled(self):
        return self._feature['enabled']

    @property
    def include_users(self):
        return self._feature['include_users']

    @property
    def exclude_users(self):
        return self._feature['exclude_users']

    @property
    def last_sync(self):
        return self._feature['last_sync']
