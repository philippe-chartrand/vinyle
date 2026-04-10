import logging
from gettext import gettext as _

from ..album import Album
from ..views import AlbumPage
from ..browsersong import BrowserSongRow


class ArtistAlbumPage(AlbumPage):
    def __init__(self, client, cache, artist_role, artist, album_name, date, folder=None, **kwargs):
        super().__init__(client, album_name, date,  **kwargs)
        tag_filter = (artist_role, artist, "album", album_name, "date", date)
        self.show_comments = kwargs.get('show_comments')
        self.show_file_format = kwargs.get('show_file_format')
        self.play_all_button.connect("clicked", lambda *args: client.filter_to_playlist(("album", album_name), "play"))
        self.play_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "play"))
        self.append_all_button.connect("clicked", lambda *args: client.filter_to_playlist(("album", album_name), "append"))
        self.append_button.connect("clicked", lambda *args: client.filter_to_playlist(tag_filter, "append"))
        self.logger = logging.getLogger(__name__)

        album = Album(album_name, date)
        album.set_selection(client, artist_role, artist, album_name, folder, tag_filter)
        if len(album.selection) == 0:
            self.logger.info("no songs found for %s %s %s %s", artist_role, artist, album_name, date)
            return
        album.expand_selection_to_all_album(client)
        if self.show_comments:
            album.add_comments(client)
        self.album_cover.set_paintable(album.get_cover(cache).get_paintable())
        self.suptitle.set_text(self.get_album_credits(album))
        self.hilite_album_year_in_date_browsing_context(artist_role, artist)
        self.set_genre_if_unique(album, artist_role)
        self.set_length_label(album.get_selection_length(), album.get_total_length())

        self.add_song_rows(artist, artist_role, album, show_comments=self.show_comments, show_file_format=self.show_file_format)

    def set_length_label(self, selection_length, total_length):
        length_text =  str(total_length) \
            if total_length._seconds == selection_length._seconds \
            else f"{selection_length} / {total_length}"
        self.length.set_text(length_text)

    def set_genre_if_unique(self, album, artist_role):
        album_genre = self.get_album_genre(album)
        if not album_genre or album_genre == _("Multiple genres"):
            self.genre.set_visible(False)
        else:
            self.genre.set_text(album_genre)
            self.genre.set_property('css_classes', ['heading']) if artist_role == 'genre' else None

    def hilite_album_year_in_date_browsing_context(self, tag_name, tag_value):
        if tag_name == 'date' and tag_value == self.subtitle.get_text():
            self.subtitle.set_property('css_classes', ['heading'])

    def add_song_rows(self, artist, artist_role, album, show_comments, show_file_format):
        show_year = self.check_for_multiple_years(album)
        show_disc = self.check_for_multiple_discs(album)
        credit_common_to_all_songs = all((self.credit_found_in_song(artist_role, artist, s) for s in album.songs))
        track_sorting = lambda s: int(100 * int(s.disc) if s.disc else 0) + int(s.track if s.track else 0)
        row_kwargs = dict(artist_to_highlight="", show_file_format=show_file_format, show_comments=show_comments)
        for song in sorted(album.songs, key=track_sorting):
            row = BrowserSongRow(
                song,
                show_track=True, show_year=show_year, show_disc=show_disc, **row_kwargs
            )
            if not credit_common_to_all_songs and self.credit_found_in_song(artist_role, artist, song):
                row.set_property('css_classes', ['activatable', 'heading'])
            self.song_list.append(row)

    @staticmethod
    def get_album_genre(album):
        if len(album.genres) == 0:
            return ""
        elif len(album.genres) == 1:
            return list(album.genres)[0]
        else:
            return _("Multiple genres")

    @staticmethod
    def get_album_credits(album):
        credits = []
        if len(album.albumartists) > 0:
            if len(album.albumartists) > 1 or (len(album.albumartists) == 1 and list(album.albumartists)[0] == 'Various Artists'):
                credits.append(_("Various artists"))
            else:
                credits.append(list(album.albumartists)[0])
        if len(album.artists) > 0:
            if len(album.artists) > 1 or (len(album.artists) == 1 and list(album.artists)[0] == 'Various Artists'):
                credits.append(_("Various artists"))
            else:
                credits.append(list(album.artists)[0])
        if len(album.composers) > 0:
            credits.append(_("Various composers") if len(album.composers) > 1 else list(album.composers)[0])
        if len(album.conductors) > 0:
            credits.append(_("Various conductors") if len(album.conductors) > 1 else list(album.conductors)[0])
        if len(album.performers) > 0:
            credits.append(_("Various performers") if len(album.performers) > 1 else list(album.performers)[0])
        return ", ".join(list(dict.fromkeys(credits)))

    @staticmethod
    def check_for_multiple_discs(album):
        if len(album.discs) == 0:
            return False
        last_disc = max(list(album.discs))
        if not last_disc.isdigit():
            return False
        return True if len(album.discs) > 1 and int(last_disc) > 1 else False

    @staticmethod
    def check_for_multiple_years(album):
        return True if len(album.years) > 1 else False

    @staticmethod
    def credit_found_in_song(role, value, song):
        credit_found = False
        if song[role][0] == value:
            credit_found = True
        elif role == 'genre' and song.genre == value:
            credit_found = True
        elif role == 'date' and song.year == value:
            credit_found = True
        return credit_found

