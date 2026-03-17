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

    def _get_albums(self, artist, role):
        grouped_albums=self._client.list("album", role, artist, "group", "date")
        albums = self.make_sure_albums_are_different(grouped_albums)
        for album in albums:
            yield RoleAlbum(artist, role, album["album"], album["date"])

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
        unique_albums = set([])
        for album in albums:
            unique_albums.add((album['album'], album['date']))
        return [dict(album=unique_album[0], date=unique_album[1]) for unique_album in list(unique_albums)]

    def _on_activate(self, widget, pos):
        album=self._selection_model.get_item(pos)
        self.emit("album-selected", album.role, album.artist, album.name, album.date)
