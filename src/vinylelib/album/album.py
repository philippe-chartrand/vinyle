import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GObject

from src.vinylelib.utils import Duration


class Album(GObject.Object):
    def __init__(self, name, date):
        GObject.Object.__init__(self)
        #minimal set
        self.name=name
        self.date=date
        self.cover=None

        # selection of songs related to browsing context
        self.selection = []
        # all songs of the album
        self.songs = []

        #used to identify unique or repeating values to avoid redundancy and hilite browsing context
        self.albumartists = set([])
        self.artists = set([])
        self.composers = set([])
        self.conductors = set([])
        self.performers = set([])
        self.genres = set([])
        self.discs = set([])
        self.years = set([])

    @property
    def year(self):
         return self.date[0:4] if len(self.date) > 3 else ""

    @property
    def year_as_int(self):
        return int(self.year) if self.year != "" else 0

    def set_selection(self, client, tag_name, tag_value, album_name, folder, tag_filter):
        if folder is None:
            self.selection=client.find(*tag_filter)
            if len(self.selection) == 0:
                # The code assumes all tracks of an album have the same date, which is not always true.
                # If the date associated with the album (often the max date) does not match with the date
                # associated with the role, relax the query criteria by ignoring the date
                self.selection = client.find(*(tag_name, tag_value, "album", album_name))
        else:
            tag_filter=(tag_name, tag_value, "album", album_name, "file", folder)
            self.selection = client.search(*tag_filter)

    def get_selection_length(self):
        return Duration(sum(s.duration._seconds for s in self.selection))

    def expand_selection_to_all_album(self, client):
        # for compilations and multiple cd albums, album title is not sufficient to find the songs
        # we need to find all songs in the same album / folder
        client.tagtypes("all")
        folders = { song.folder for song in self.selection }
        for folder in sorted(folders):
            self.songs.extend(client.get_albums_songs_by_common_folder(folder))
        self._check_for_multiple_values()

    def get_cover(self, cache):
        return cache.get_cover(self.songs[0].file)
    
    def get_total_length(self):
        return Duration(sum(s.duration._seconds for s in self.songs))
    
    def _check_for_multiple_values(self):
        for s in self.songs:
            self.albumartists.add(s.albumartist) if bool(s.albumartist) else None
            self.artists.add(s.artist) if bool(s.artist) else None
            self.composers.add(s.composer) if bool(s.composer) else None
            self.conductors.add(s.conductor) if bool(s.conductor) else None
            self.performers.add(s.performer) if bool(s.performer) else None
            self.genres.add(s.genre) if bool(s.genre) else None
            self.discs.add(s.disc) if bool(s.disc) else None
            self.years.add(s.year) if bool(s.year) else None

