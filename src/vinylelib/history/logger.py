import datetime
import logging
from math import floor

from ..song import Song


class HistoryLogger(object):
    HISTORY_PLAYLIST_NAME = 'Historique'
    def __init__(self, client, log_to_playlist=False):
        self._client = client
        self.log_to_playlist = log_to_playlist
        self.logger = logging.getLogger(__name__)
        self._client.emitter.connect("current-song", self._log_one)
        self._client.emitter.connect("elapsed", self._on_elapsed)
        self.current = None
        self.elapsed = None
        self.duration = None

    def _on_elapsed(self, emitter, elapsed, duration):
        progress = round(100.0 * elapsed / duration)
        self.logger.debug("%s, elapsed %s", datetime.datetime.now(), progress)
        self.elapsed = elapsed
        self.duration = duration

    def _log_one(self, emitter, song, songpos, songid, state):
        # current must be either None or song, not {}
        if self.current is None:
            self.current = song if bool(song) else None
        else:
            if self.elapsed >= floor(self.duration):
                self.logger.info('%s, Song "%s" has played', datetime.datetime.now(), self.current.title)
                if self.log_to_playlist:
                    self._client.playlistadd(self.HISTORY_PLAYLIST_NAME, self.current.file)
                self.current = song if bool(song) else None