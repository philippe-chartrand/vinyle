import collections
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, GObject

from ..duration import Duration
from ..multitag import MultiTag

class SongMetaclass(type(GObject.Object), type(collections.UserDict)):
    pass


class Song(collections.UserDict, GObject.Object, metaclass=SongMetaclass):
    widget=GObject.Property(type=Gtk.Widget, default=None)  # current widget representing the song in the UI
    def __init__(self, data):
        collections.UserDict.__init__(self, data)
        GObject.Object.__init__(self)

    @property
    def year(self):
        return self.data['date'][0][0:4] if 'date' in self.data else None

    @property
    def date(self):
        return self.data['date'][0] if 'date' in self.data else None

    @property
    def album(self):
        return self.data['album'][0] if 'album' in self.data else None

    @property
    def title(self):
        return self.data['title'][0] if 'title' in self.data else None

    @property
    def disc(self):
        return self.data['disc'][0] if 'disc' in self.data else None

    @property
    def track(self):
        return self.data['track'][0] if 'track' in self.data else None

    @property
    def file(self):
        return self.data['file'] if 'file' in self.data else None

    @property
    def duration(self):
        return self.data['duration'] if 'duration' in self.data else None

    @property
    def pos(self):
        return self.data['pos'] if 'pos' in self.data else None

    @property
    def id(self):
        return self.data['id'] if 'id' in self.data else None

    @property
    def albumartist(self):
        return self.data['albumartist'][0] if 'albumartist' in self.data else None

    @property
    def artist(self):
        return self.data['artist'][0] if 'artist' in self.data else None

    @property
    def composer(self):
        return self.data['composer'][0] if 'composer' in self.data else None

    @property
    def conductor(self):
        return self.data['conductor'][0] if 'conductor' in self.data else None

    @property
    def performer(self):
        return self.data['performer'][0] if 'performer' in self.data else None

    @property
    def albumartists(self):
        return self.data['albumartist'] if 'albumartist' in self.data else ()

    @property
    def artists(self):
        return self.data['artist'] if 'artist' in self.data else ()

    @property
    def composers(self):
        return self.data['composer'] if 'composer' in self.data else ()

    @property
    def conductors(self):
        return self.data['conductor'] if 'conductor' in self.data else ()

    @property
    def performers(self):
        return self.data['performer'] if 'performer' in self.data else ()

    def __setitem__(self, key, value):
        if key == "time":  # time is deprecated https://mpd.readthedocs.io/en/latest/protocol.html#other-metadata
            pass
        elif key == "duration":
            super().__setitem__(key, Duration(value))
        elif key in ("range", "file", "pos", "id", "format", "last-modified"):
            super().__setitem__(key, value)
        else:
            if isinstance(value, list):
                super().__setitem__(key, MultiTag(value))
            else:
                super().__setitem__(key, MultiTag([value]))

    def __missing__(self, key):
        if self.data:
            if key == "albumartist":
                return self["artist"]
            elif key == "albumartistsort":
                return self["albumartist"]
            elif key == "artistsort":
                return self["artist"]
            elif key == "title":
                return MultiTag([GLib.path_get_basename(self.data["file"])])
            elif key == "duration":
                return Duration()
            else:
                return MultiTag([""])
        else:
            return None

    def define_subtitle(self, artist_to_highlight=None, delim="\r"):
        artist_subtitle = ", ".join(artist for artist in self.artists)
        composer_subtitle = ", ".join(composer for composer in self.composers)
        conductor_subtitle = ", ".join(conductor for conductor in self.conductors)
        performer_subtitle = ", ".join(performer for performer in self.performers)
        subtitle = ""
        credits = []
        found_in_credits = False
        if artist_subtitle:
            credits.append(artist_subtitle)
        if composer_subtitle:
            credits.append(composer_subtitle)
        if conductor_subtitle:
            credits.append(conductor_subtitle)
        if performer_subtitle:
            credits.append(performer_subtitle)
        if bool(credits):
            subtitle = delim.join(list(dict.fromkeys(credits))) #remove duplicates but keep ordering
            if artist_to_highlight in credits:
                found_in_credits = True
        return subtitle, found_in_credits
