from ..album import AlbumListRow
from ..client.cover import FallbackCover


class RoleAlbumListRow(AlbumListRow):
    def __init__(self, client):
        super().__init__(client)

    def set_album(self, album, **kwargs):
        super().set_album(album)
        if album.cover is None:
            self._client.tagtypes("clear")
            song=self._client.find(album.role, album.artist, "album", album.name, "date", album.date, "window", "0:1")[0]
            self._client.tagtypes("all")
            if 'album_cover_size' in kwargs and kwargs['album_cover_size'] == 'no-cover':
                album.cover=FallbackCover().get_paintable()
            else:
                album.cover=self._client.get_cover(song.file).get_paintable()
        self._cover.set_paintable(album.cover)