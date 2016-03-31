# -*- coding: utf-8 -*-

class Feature(object):

    def __init__(self, key, enabled, rollout_progress=0, rollout_target=0, include_users=[], exclude_users=[], last_sync=None):
        self._feature = {
            'key': key,
            'enabled': enabled,
            'rollout_progress': rollout_progress,
            'rollout_target': rollout_target,
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
    def rollout_progress(self):
        return self._feature['rollout_progress']

    @property
    def rollout_target(self):
        return self._feature['rollout_target']

    @property
    def include_users(self):
        return self._feature['include_users']

    @property
    def exclude_users(self):
        return self._feature['exclude_users']

    @property
    def last_sync(self):
        return self._feature['last_sync']
