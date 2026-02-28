import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, GObject, Gtk
from gettext import gettext as _

from ..album import AlbumsPage
from ..artist_album import ArtistAlbum
from ..artist_album import ArtistAlbumListRow


class ArtistAlbumsPage(AlbumsPage):
    __gsignals__={"album-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,str,str,str,))}
    def __init__(self, client, settings):
        super().__init__(client, settings, ArtistAlbum, ArtistAlbumListRow, _("Select an artist"))

    def _get_albums(self, artist, role):

        grouped_albums=self._client.list("album", role, artist, "group", "date")
        albums = self.group_albums_dates(grouped_albums)
        for album in albums.values():
            yield ArtistAlbum(artist, role, album["album"], album["date"])

    def group_albums_dates(self, grouped_albums):
        albums = {}
        for album in grouped_albums:
            if album['album'] in albums:
                if album['date'][0:4] > albums[album['album']]['date'][0:4]:
                    albums[album['album']]['date'] = album['date']
            else:
                albums[album['album']] = album
        return albums

    def _on_activate(self, widget, pos):
        album=self._selection_model.get_item(pos)
        self.emit("album-selected", album.role, album.artist, album.name, album.date)