import datetime
import logging
from collections import OrderedDict

from .fallback import FallbackCover
from ..utils import total_size
"""
Implements a LRU cache with an Ordered Dict
Expect a memory usage of 130 000 000 bytes for 1000 600x600 covers
"""

class CoverCache(object):

    def __init__(self, client, cache_size):
        super().__init__()
        self._cache = OrderedDict()
        self._client = client
        assert cache_size.isdigit(), "cover cache size should be an integer value"
        self.MAX_ITEMS = int(cache_size)
        self.log = False
        self.logger = logging.getLogger(__name__)

    def _enforce_limits(self):
        if len(self._cache) >= self.MAX_ITEMS:
            self._cache.popitem(last=False)

    def get_cover(self, uri):
        self._log_info(uri)

        if uri in self._cache:
            self._log_debug('from cache')
            return self._cache[uri]
        else:
            self._enforce_limits()
            cover = self._client.get_cover(uri)
            if cover is None:
                self._log_debug('no cover found')
                return FallbackCover()
            else:
                self._cache[uri] = cover
                self._log_debug('from server')
                return cover

    def _log_info(self, message):
        if self.log:
            self.logger.info("%s, %s, n:%s, size:%s", datetime.datetime.now(), message, len(self._cache),total_size(self._cache))

    def _log_debug(self, message):
        if self.log:
            self.logger.debug("%s, %s, n:%s, size:%s", datetime.datetime.now(), message, len(self._cache),total_size(self._cache))

    def clear(self):
        self._cache = {}