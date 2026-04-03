import datetime
import logging


class HistoryLogger(object):
    HISTORY_PLAYLIST_NAME = 'Historique'
    def __init__(self, client):
        self._client = client
        self.logger = logging.getLogger(__name__)
        self._client.emitter.connect("current-song", self._logOne)
        self._client.emitter.connect("elapsed", self._on_elapsed)
        self.current = None
        self.elapsed = None
        self.duration = None

    def _on_elapsed(self, emitter, elapsed, duration):
        progress = round(100.0 * elapsed / duration)
        self.logger.debug("%s, elapsed %s", datetime.datetime.now(), progress)
        self.elapsed = elapsed
        self.duration = duration

    def _logOne(self, emitter, song, songpos, songid, state):
        if self.current is not None:
            if round(self.elapsed) >= round(self.duration):
                self.logger.info('%s, Song "%s" has played', datetime.datetime.now(), self.current.title)
                self._client.playlistadd(self.HISTORY_PLAYLIST_NAME, self.current.file)
        self.current = song