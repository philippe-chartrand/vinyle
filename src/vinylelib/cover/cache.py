import datetime
from .fallback import FallbackCover

class CoverCache(object):
    __print_usage_to_stdout = False  # For debug purposes. Set to True if you want to monitor creation and destruction

    def __init__(self, client):
        super().__init__()
        self._cache = {}
        self._client = client

    def get_cover(self, uri):
        if uri in self._cache:
            self._log_usage('from cache')
            return self._cache[uri]
        else:
            cover = self._client.get_cover(uri)
            if cover is None:
                self._log_usage('no cover found')
                return FallbackCover()
            else:
                self._cache[uri] = cover
                self._log_usage('from server')
                return cover

    def _log_usage(self, message):
        if self.__print_usage_to_stdout:
            print(datetime.datetime.now(), message, len(self._cache))

    def clear(self):
        self._cache = {}