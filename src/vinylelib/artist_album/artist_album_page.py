from ..album import AlbumPage
from ..browsersong import BrowserSongRow
from ..duration import Duration


class ArtistAlbumPage(AlbumPage):
    def __init__(self, client, artist_role, albumartist, album, date):
        super().__init__(client, album, date)
        tag_filter = ("album", album)

        self.play_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "play"))
        self.append_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "append"))

        self.suptitle.set_text(albumartist)
        self.length.set_text(str(Duration(client.count(*tag_filter)["playtime"])))
        client.restrict_tagtypes("track", "title", "artist", "date")
        songs=client.find(*tag_filter)
        client.tagtypes("all")
        self.album_cover.set_paintable(client.get_cover(songs[0]["file"]).get_paintable())
        show_year = False
        dates = {s['date'][0][0:3] for s in songs}
        artists = {s['albumartist'][0] for s in songs}

        if len(dates) > 1:
            show_year = True
        for song in songs:
            artist_to_highlight = ""
            if song['artist'][0] == albumartist and len(artists) > 1:
                artist_to_highlight = albumartist
            row=BrowserSongRow(song, artist_to_highlight=artist_to_highlight, show_year=show_year)
            self.song_list.append(row)