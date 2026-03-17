from gettext import gettext as _

from ..views import AlbumPage
from ..browsersong import BrowserSongRow
from ..utils import Duration


class ArtistAlbumPage(AlbumPage):
    def __init__(self, client, cache, artist_role, artist, album, date, folder=None, **kwargs):
        super().__init__(client, album, date,  **kwargs)
        tag_filter = (artist_role, artist, "album", album, "date", date)
        self.play_all_button.connect("clicked", lambda *args: client.filter_to_playlist(("album", album), "play"))
        self.play_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "play"))
        self.append_all_button.connect("clicked", lambda *args: client.filter_to_playlist(("album", album), "append"))
        self.append_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "append"))

        if folder is None:
            artist_album_songs=client.find(*tag_filter)
        else:
            tag_filter=(artist_role, artist, "album", album, "file", folder)
            artist_album_songs = client.search(*tag_filter)

        selection_length = Duration(sum(s.duration._seconds for s in artist_album_songs))
        if len(artist_album_songs) == 0:
            return
        client.tagtypes("all")
        songs = self.expand_songs_for_all_album(client, artist_album_songs)
        total_length = Duration(sum(s.duration._seconds for s in songs))
        self.album_cover.set_paintable(cache.get_cover(songs[0].file).get_paintable())
        self.length.set_text(str(total_length)) if total_length._seconds == selection_length._seconds \
            else self.length.set_text(f"{selection_length} / {total_length}")
        self.set_genre_if_unique(songs)
        self.suptitle.set_text(self._define_artist_credits_supertitle(songs))
        dates = self.roundup_dates_to_year(songs)
        show_disc = self.check_for_multiple_discs(songs)
        show_year = True if len(dates) > 1 else False

        # songs
        for song in sorted(songs, key=lambda s:int(100 * int(s.disc) if s.disc else 0) + int(s.track if s.track else 0)):
            artist_to_highlight = self.artist_name_to_hilite(artist, artist_role, song.all_artists, song)
            row=BrowserSongRow(song, artist_to_highlight=artist_to_highlight, show_year=show_year, show_disc=show_disc)
            self.song_list.append(row)

    def set_genre_if_unique(self, songs):
        album_genre = self.get_album_genre(songs)
        if not album_genre or album_genre == _("Multiple genres"):
            self.genre.set_visible(False)
        else:
            self.genre.set_text(album_genre)

    @staticmethod
    def get_album_genre(songs):
        genres = { s.genre for s in songs }
        if len(genres) == 0:
            return ""
        elif len(genres) == 1:
            return list(genres)[0]
        else:
            return _("Multiple genres")

    def _define_artist_credits_supertitle(self, songs):
        albumartists = self.list_album_artists_as_a_set('albumartist', songs)
        artists = self.list_album_artists_as_a_set('artist', songs)
        composers = self.list_album_artists_as_a_set('composer', songs)
        conductors = self.list_album_artists_as_a_set('conductor', songs)
        performers = self.list_album_artists_as_a_set('performer', songs)
        credits = []
        if len(albumartists) > 0 and len(albumartists[0]) > 0:
            if len(albumartists) > 1 or (len(albumartists) == 1 and albumartists[0] == 'Various Artists'):
                credits.append(_("Various artists"))
            else:
                credits.append(albumartists[0])
        if len(artists) > 0 and len(artists[0]) > 0:
            if len(artists) > 1 or (len(artists) == 1 and artists[0] == 'Various Artists'):
                credits.append(_("Various artists"))
            else:
                credits.append(artists[0])
        if len(composers) > 0 and len(composers[0]) > 0:
            credits.append(_("Various composers") if len(composers) > 1 else composers[0])
        if len(conductors) > 0 and len(conductors[0]) > 0:
            credits.append(_("Various conductors") if len(conductors) > 1 else conductors[0])
        if len(performers) > 0 and len(performers[0]) > 0:
            credits.append(_("Various performers") if len(performers) > 1 else performers[0])
        return ", ".join(list(dict.fromkeys(credits)))

    def list_album_artists_as_a_set(self, artist_role, songs):
        artists = {s[artist_role][0] for s in songs if s[artist_role[0]] != "" }
        return list(artists)

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
        if song[artist_role][0] == albumartist and len(artists) > 0:
            artist_to_highlight = albumartist
        return artist_to_highlight

    def expand_songs_for_all_album(self, client, artist_album_songs):
        # for compilations and multiple cd albums, album title is not sufficient to find the songs
        # we need to find all songs in the same album / folder

        folders = { song.folder for song in artist_album_songs }
        songs = []
        for folder in sorted(folders):
            songs.extend(client.get_albums_songs_by_common_folder(folder))
        return songs