import itertools

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject
from gettext import gettext as _

from .browsersong import BrowserSongList, BrowserSongRow
from .artist_album import ArtistAlbumRow


class SearchView(Gtk.Stack):
    __gsignals__={
        "album-artist-selected": (GObject.SignalFlags.RUN_FIRST, None, (str, str,)),
        "artist-selected": (GObject.SignalFlags.RUN_FIRST, None, (str, str,)),
        "composer-selected": (GObject.SignalFlags.RUN_FIRST, None, (str, str,)),
        "conductor-selected": (GObject.SignalFlags.RUN_FIRST, None, (str, str, )),
        "performer-selected": (GObject.SignalFlags.RUN_FIRST, None, (str, str,)),
        "album-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,str,str,))
    }

    def __init__(self, client):
        super().__init__()
        self._client=client

        self.RESULTS_COUNT = 5
        self.RESULTS_COUNT_ALBUM = 10
        self.RESULTS_COUNT_SONG = 20
        self.MIN_CHARS_FOR_SEARCH = 3
        self._song_tags=("title", "artist", "composer",  "conductor",  "performer", "album", "date")
        self._album_artist_tags=("albumartist", "albumartistsort")
        self._artist_tags=("artist", "artistsort")
        self._composer_tags=("composer", "composer")
        self._conductor_tags=("conductor", "conductor")
        self._performer_tags=("performer", "performer")
        self._album_tags=("album", "albumartist", "albumartistsort", "date")

        # artist list
        self._album_artist_list = self._init_list_box()
        self._artist_list = self._init_list_box()
        self._composer_list = self._init_list_box()
        self._conductor_list = self._init_list_box()
        self._performer_list = self._init_list_box()

        # album list
        self._album_list = self._init_list_box()

        # song list
        self._song_list=BrowserSongList(client, show_album=True)
        self._song_list.add_css_class("boxed-list")

        # boxes
        self._album_artist_box = self._init_box("Album Artists", self._album_artist_list)
        self._artist_box = self._init_box("Artists", self._artist_list)
        self._composer_box = self._init_box("Composers", self._composer_list)
        self._conductor_box = self._init_box("Conductors", self._conductor_list)
        self._performer_box = self._init_box("Performers", self._performer_list)

        self._album_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._album_box.append(Gtk.Label(label=_("Albums"), xalign=0, css_classes=["heading"]))
        self._album_box.append(self._album_list)

        self._song_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._song_box.append(Gtk.Label(label=_("Songs"), xalign=0, css_classes=["heading"]))
        self._song_box.append(self._song_list)

        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30, margin_start=12, margin_end=12, margin_top=24, margin_bottom=24)
        box.append(self._album_artist_box)
        box.append(self._artist_box)
        box.append(self._composer_box)
        box.append(self._conductor_box)
        box.append(self._performer_box)
        box.append(self._album_box)
        box.append(self._song_box)
        self.box = box

        # scroll
        scroll=Gtk.ScrolledWindow(child=Adw.Clamp(child=box))
        self._adj=scroll.get_vadjustment()

        # status page
        status_page=Adw.StatusPage(icon_name="edit-find-symbolic", title=_("No Results"), description=_("Try a different search"))

        # connect
        self._album_artist_list.connect("row-activated", self._on_album_artist_activate)
        self._artist_list.connect("row-activated", self._on_artist_activate)
        self._composer_list.connect("row-activated", self._on_composer_activate)
        self._conductor_list.connect("row-activated", self._on_conductor_activate)
        self._performer_list.connect("row-activated", self._on_performer_activate)

        self._album_artist_list.connect("keynav-failed", self._on_keynav_failed)
        self._artist_list.connect("keynav-failed", self._on_keynav_failed)
        self._composer_list.connect("keynav-failed", self._on_keynav_failed)
        self._conductor_list.connect("keynav-failed", self._on_keynav_failed)
        self._performer_list.connect("keynav-failed", self._on_keynav_failed)

        self._album_list.connect("row-activated", self._on_album_activate)
        self._album_list.connect("keynav-failed", self._on_keynav_failed)

        # packing
        self.add_named(status_page, "no-results")
        self.add_named(scroll, "results")

    @staticmethod
    def _init_list_box():
        list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, tab_behavior=Gtk.ListTabBehavior.ITEM,
                                        valign=Gtk.Align.START)
        list_box.add_css_class("boxed-list")
        return list_box

    @staticmethod
    def _init_box(label, list_):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(Gtk.Label(label=_(label), xalign=0, css_classes=["heading"]))
        box.append(list_)
        return box

    def clear(self):
        self._album_artist_list.remove_all()
        self._artist_list.remove_all()
        self._composer_list.remove_all()
        self._conductor_list.remove_all()
        self._performer_list.remove_all()
        self._album_list.remove_all()
        self._song_list.remove_all()
        self._adj.set_value(0.0)
        self.set_visible_child_name("no-results")

    def search(self, search_text):
        self.clear()
        if len(search_text)  < self.MIN_CHARS_FOR_SEARCH:
            self.box.set_visible(False)
        if len(search_text) >= self.MIN_CHARS_FOR_SEARCH and (keywords:=search_text.split()):
            self.box.set_visible(True)
            self._client.restrict_tagtypes(*self._song_tags)
            songs=self._client.search(self._client.get_search_expression(self._song_tags, keywords), "window", f"0:{self.RESULTS_COUNT_SONG}")
            self._client.tagtypes("all")
            for song in songs:
                row=BrowserSongRow(song, show_track=False)
                self._song_list.append(row)
            self._song_box.set_visible(self._song_list.get_first_child() is not None)

            albums=self._client.list("album", self._client.get_search_expression(self._album_tags, keywords), "group", "date", "group", "albumartist", "group", "composer")
            for album in itertools.islice(albums, self.RESULTS_COUNT_ALBUM):
                album_row = ArtistAlbumRow(album)
                self._album_list.append(album_row)

            self._album_box.set_visible(self._album_list.get_first_child() is not None)

            self.list_by_album_artist(keywords)
            self.list_by_artist(keywords)
            self.list_by_composer(keywords)
            self.list_by_conductor(keywords)
            self.list_by_performer(keywords)

        if (self._song_box.get_visible()
                or self._album_artist_box.get_visible()
                or self._album_box.get_visible()
                or self._artist_box.get_visible()
                or self._composer_box.get_visible()
                or self._conductor_box.get_visible()
                or self._performer_box.get_visible()):
            self.set_visible_child_name("results")

    def _list_by(self, tag, keywords, tags, list_, box):
        items = self._client.list(tag, self._client.get_search_expression(tags, keywords))
        for item in itertools.islice(items, self.RESULTS_COUNT):
            row = Adw.ActionRow(title=item[tag], use_markup=False, activatable=True)
            row.add_suffix(Gtk.Image(icon_name="go-next-symbolic", accessible_role=Gtk.AccessibleRole.PRESENTATION))
            list_.append(row)
        found = list_.get_first_child() is not None
        box.set_visible(list_.get_first_child() is not None)
        return list_, box

    def list_by_album_artist(self, keywords):
        self._album_artist_list, self._album_artist_box = self._list_by("albumartist", keywords, self._album_artist_tags,
                                                            self._album_artist_list, self._album_artist_box)
    def list_by_artist(self, keywords):
        self._artist_list, self._artist_box = self._list_by("artist", keywords, self._artist_tags, self._artist_list, self._artist_box)

    def list_by_composer(self, keywords):
        self._composer_list, self._composer_box = self._list_by("composer", keywords, self._composer_tags, self._composer_list, self._composer_box)

    def list_by_conductor(self, keywords):
        self._conductor_list, self._conductor_box = self._list_by("conductor", keywords, self._conductor_tags, self._conductor_list, self._conductor_box)

    def list_by_performer(self, keywords):
        self._performer_list, self._performer_box = self._list_by("performer", keywords, self._performer_tags, self._performer_list, self._performer_box)

    def _on_album_artist_activate(self, list_box, row):
        self.emit("artist-selected", row.get_title(), 'albumartist')

    def _on_artist_activate(self, list_box, row):
        self.emit("artist-selected", row.get_title(), 'artist')

    def _on_composer_activate(self, list_box, row):
        self.emit("artist-selected", row.get_title(), 'composer')

    def _on_conductor_activate(self, list_box, row):
        self.emit("artist-selected", row.get_title(), 'conductor')

    def _on_performer_activate(self, list_box, row):
        self.emit("artist-selected", row.get_title(), 'performer')

    def _on_album_activate(self, list_box, row):
        self.emit("album-selected", row.album, row.artist, row.date)

    def _on_keynav_failed(self, list_box, direction):
        if (root:=list_box.get_root()) is not None:
            if direction == Gtk.DirectionType.UP:
                root.child_focus(Gtk.DirectionType.TAB_BACKWARD)
            elif direction == Gtk.DirectionType.DOWN:
                root.child_focus(Gtk.DirectionType.TAB_FORWARD)