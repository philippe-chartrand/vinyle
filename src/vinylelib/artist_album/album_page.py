from os.path import dirname

from ..album import AlbumPage
from ..browsersong import BrowserSongRow
from ..duration import Duration


class ArtistAlbumPage(AlbumPage):
    def __init__(self, client, artist_role, artist, album, date, file):
        super().__init__(client, album, date)
        tag_filter=(artist_role, artist, "album", album, "file", file)

        self.play_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "play"))
        self.append_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "append"))

        self.suptitle.set_text(f"{artist_role}: {artist}")
        self.length.set_text(str(Duration(client.count(*tag_filter)["playtime"])))
        client.restrict_tagtypes("track", "disc", "title", "albumartist", "artist", "composer", "conductor", "date")
        artist_album_songs=client.find(*tag_filter)
        if len(artist_album_songs) == 0:
            return
        songs = self.expand_songs_for_all_album(client, artist_album_songs)
        client.tagtypes("all")
        self.album_cover.set_paintable(client.get_cover(songs[0]["file"]).get_paintable())
        show_year = False
        dates = self.roundup_dates_to_year(songs)
        artists = self.list_album_artists(artist_role, songs)
        show_disc = self.check_for_multiple_discs(songs)

        if len(dates) > 1:
            show_year = True
        for song in sorted(songs, key=lambda s:int(100 * int(s.disc) if s.disc else 0) + int(s.track if s.track else 0)):
            artist_to_highlight = self.artist_name_to_hilite(artist, artist_role, artists, song)
            row=BrowserSongRow(song, artist_to_highlight=artist_to_highlight, show_year=show_year, show_disc=show_disc)
            self.song_list.append(row)

    def list_album_artists(self, artist_role, songs):
        artists = {s[artist_role][0] for s in songs}
        return artists

    def  check_for_multiple_discs(self, songs):
        discs = max([s['disc'][0] for s in songs])
        if not discs.isdigit():
            return False
        return True if int(discs) > 1 else False

    def roundup_dates_to_year(self, songs):
        years = {s.year for s in songs if s.year is not None}
        return years

    def artist_name_to_hilite(self, albumartist, artist_role, artists, song):
        artist_to_highlight = ""
        if song[artist_role][0] == albumartist and len(artists) > 1:
            artist_to_highlight = albumartist
        return artist_to_highlight

    def expand_songs_for_all_album(self, client, artist_album_songs):
        # for compilations and multiple cd albums, album title is not sufficient to find the songs
        directories = { dirname(song.file) for song in artist_album_songs }
        songs = []
        for directory in sorted(directories):
            songs.extend(client.get_albums_songs_by_common_directory(directory))
        return songs