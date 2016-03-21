# -*- coding: utf-8 -*-

import time

class Feature(object):

    def __init__(self, key, enabled, include_users=[], exclude_users=[]):
        self._feature = {
            'key': key,
            'enabled': enabled,
            'include_users': include_users,
            'exclude_users': exclude_users,
            'created': int(time.time())
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
    def created(self):
        return self._feature['created']
