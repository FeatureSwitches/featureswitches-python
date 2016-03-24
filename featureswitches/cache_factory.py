# -*- coding: utf-8 -*-

import os, tempfile

from dogpile.cache import make_region

def cache_factory(cachefile=None):
    if not cachefile:
        cachefile = os.path.join(tempfile.gettempdir(), 'featureswitches.cache')

    if os.path.isfile(cachefile):
        os.remove(cachefile)

    region = make_region()
    region.configure(
            'dogpile.cache.dbm',
            expiration_time=0,
            arguments = {
                'filename': cachefile,
            }
        )

    return region

