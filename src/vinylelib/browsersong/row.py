import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


class BrowserSongRow(Adw.ActionRow):
    def __init__(self, song, show_track=True, show_year=True, show_disc=False, artist_to_highlight="", **kwargs):
        super().__init__(use_markup=False, activatable=True, **kwargs)
        self.song=song

        # populate
        self.set_title(song.title)
        self.define_and_set_subtitle(artist_to_highlight, song)
        length=Gtk.Label(label=str(song.duration), xalign=1, single_line_mode=True, css_classes=["numeric", "dimmed"])
        self.add_suffix(length)
        if show_year:
            year = Gtk.Label(label=str(song.year if song.year is not None else "[----]"), xalign=1, single_line_mode=True, css_classes=["numeric"])
            self.add_suffix(year)
        if show_track:
            if show_disc and song.disc is not None:
                disc_and_track = f"{song.disc}-{song.track}"
            else:
                disc_and_track = song.track

            track=Gtk.Label(label=disc_and_track, xalign=1, single_line_mode=True, width_chars=3, css_classes=["numeric", "dimmed"])
            self.add_prefix(track)

    def define_and_set_subtitle(self, artist_to_highlight, song):
        subtitle, found_in_credit = song.define_subtitle(artist_to_highlight)
        if subtitle:
            if found_in_credit:
                self.set_property('css_classes', ['activatable', 'heading'])
            self.set_subtitle(subtitle)
