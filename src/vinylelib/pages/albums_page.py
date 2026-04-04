import datetime
import logging
from collections import OrderedDict

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject
from gettext import gettext as _

from ..views import AlbumsPage
from ..role_album import RoleAlbum
from ..role_album import RoleAlbumListRow


class ArtistAlbumsPage(AlbumsPage):
    __gsignals__={"album-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,str,str,str,))}
    def __init__(self, client, cache, settings):
        super().__init__(client, cache, settings, RoleAlbum, RoleAlbumListRow, _("Select an artist"))
        self.logger = logging.getLogger(__name__)
        self.MAX_PLAYLIST_ITEMS = settings.get_int('max-number-of-playlist-items')
        self.MAX_ALBUMS = settings.get_int('max-number-of-albums')

    def _get_albums(self, artist, role):
        grouped_albums = self.get_grouped_albums(artist, role)
        albums = self.make_sure_albums_are_different(grouped_albums)
        if len(albums) == 0:
            # example case: an album without a name:
            # grouped_albums will be [{'album': '', 'date': ''}]
            # albums will therefore be []
            self.logger.warning("%s, no albums found for %s «%s»", datetime.datetime.now(), role, artist)
            return

        for album in albums:
            yield RoleAlbum(artist, role, album["album"], album["date"])

    def get_grouped_albums(self, artist, role):
        if role == 'playlist':
            grouped_albums = self.playlist_albums(self._client.listplaylist(artist, f"0:{self.MAX_PLAYLIST_ITEMS}"), artist)
        else:
            grouped_albums = self._client.list("album", role, artist, "group", "date")
        if len(grouped_albums) >= self.MAX_ALBUMS:
            self.logger.warning("%s, number of albums has been limited to %s albums",  datetime.datetime.now(), self.MAX_ALBUMS)
        return grouped_albums[0:self.MAX_ALBUMS]

    def group_albums_dates_by_album_name(self, grouped_albums):
        albums_dates = {}
        for album in grouped_albums:
            if album['album'] == "":
                continue
            year = album['date'][0:4]
            if year == "":
                continue
            if album['album'] in albums_dates:
                albums_dates[album['album']].append(year)
            else:
                albums_dates[album['album']] = [year]
        return albums_dates

    def make_sure_albums_are_different(self, grouped_albums):
        dates_per_album = self.group_albums_dates_by_album_name(grouped_albums)
        albums = []
        for album in grouped_albums:
            if album['album'] == "":
                continue
            if album['album'] in dates_per_album and len(dates_per_album[album['album']]) > 1:
                self.identify_different_albums_with_same_name(album, albums)
            else:
                albums.append(album)
        return self.make_unique(albums)

    def identify_different_albums_with_same_name(self, album, albums):
        distinct_albums = {}
        for s in self._client.find('album', album['album']):
            if s.folder in distinct_albums.keys():
                distinct_albums[s.folder].add((s.album, s.year))
            else:
                distinct_albums[s.folder] = {(s.album, s.year)}
        for folder in distinct_albums:
                album_name = list(distinct_albums[folder])[0][0]
                years = [item[1] for item in list(distinct_albums[folder]) if item[1] is not None]
                year = max(years) if bool(years) else ""
                albums.append(dict(album=album_name, date=year))

    def make_unique(self, albums):
        unique_albums = OrderedDict()
        for album in albums:
            key = (album['album'], album['date'])
            if not key in unique_albums:
                unique_albums[key] = 1
        return [dict(album=key[0], date=key[1]) for key in unique_albums.keys()]

    def playlist_albums(self, playlist, playlist_name):
        albums = []
        seen_albums = set([])
        if len(playlist) == self.MAX_PLAYLIST_ITEMS:
            self.logger.warning("%s, Playlist %s has been limited to the first %s items",  datetime.datetime.now(), playlist_name, self.MAX_PLAYLIST_ITEMS)
        for item in playlist:
            album_infos = self._client.list('album','file',item, "group","date")
            if len(album_infos) > 0:
                t = (album_infos[0]['album'], album_infos[0]['date'])
                if t not in seen_albums:
                    seen_albums.add(t)
                    albums.append(album_infos[0])
        return albums

    def _on_activate(self, widget, pos):
        album=self._selection_model.get_item(pos)
        self.emit("album-selected", album.role, album.artist, album.name, album.date)
