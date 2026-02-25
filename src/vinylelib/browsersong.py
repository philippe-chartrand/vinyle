import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, Gio, Gtk, Graphene
from .song import SongMenu, define_subtitle
from .functions import lookup_icon

class BrowserSongRow(Adw.ActionRow):
    def __init__(self, song, show_track=True, show_year=True, show_disc=False, artist_to_highlight="", **kwargs):
        super().__init__(use_markup=False, activatable=True, **kwargs)
        self.song=song

        # populate
        self.set_title(song["title"][0])
        self.define_and_set_subtitle(artist_to_highlight, song)
        length=Gtk.Label(label=str(song["duration"]), xalign=1, single_line_mode=True, css_classes=["numeric", "dimmed"])
        self.add_suffix(length)
        if show_year:
            year_from_date = song["date"][0][0:4]
            year = Gtk.Label(label=str(year_from_date), xalign=1, single_line_mode=True, css_classes=["numeric"])
            self.add_suffix(year)
        if show_track:
            if show_disc and song["disc"] is not None:
                disc = song['disc'][0]
                track =  song['track'][0]
                disc_and_track = f"{disc}-{track}"
            else:
                disc_and_track = song["track"][0]

            track=Gtk.Label(label=disc_and_track, xalign=1, single_line_mode=True, width_chars=3, css_classes=["numeric", "dimmed"])
            self.add_prefix(track)

    def define_and_set_subtitle(self, artist_to_highlight, song):
        subtitle, found_in_credit = define_subtitle(song, artist_to_highlight)
        if subtitle:
            if found_in_credit:
                self.set_property('css_classes', ['activatable', 'heading'])
            self.set_subtitle(subtitle)


class BrowserSongList(Gtk.ListBox):
    def __init__(self, client, show_album=False):
        super().__init__(selection_mode=Gtk.SelectionMode.NONE, tab_behavior=Gtk.ListTabBehavior.ITEM, valign=Gtk.Align.START)
        self._client=client

        # menu
        self._menu=SongMenu(client, show_album=show_album)

        # action group
        action_group=Gio.SimpleActionGroup()
        action=Gio.SimpleAction.new("menu", None)
        action.connect("activate", self._on_menu)
        action_group.add_action(action)
        self.insert_action_group("view", action_group)

        # shortcuts
        self.add_shortcut(Gtk.Shortcut.new(Gtk.KeyvalTrigger.new(Gdk.KEY_Menu, 0), Gtk.NamedAction.new("view.menu")))
        self.add_shortcut(Gtk.Shortcut.new(Gtk.KeyvalTrigger.new(Gdk.KEY_F10, Gdk.ModifierType.SHIFT_MASK), Gtk.NamedAction.new("view.menu")))

        # event controller
        button_controller=Gtk.GestureClick(button=0)
        self.add_controller(button_controller)
        long_press_controller=Gtk.GestureLongPress()
        self.add_controller(long_press_controller)
        drag_source=Gtk.DragSource()
        drag_source.set_icon(lookup_icon("audio-x-generic", 32, self.get_scale_factor()), 0, 0)
        self.add_controller(drag_source)

        # connect
        self.connect("row-activated", self._on_row_activated)
        self.connect("keynav-failed", self._on_keynav_failed)
        button_controller.connect("pressed", self._on_button_pressed)
        long_press_controller.connect("pressed", self._on_long_pressed)
        drag_source.connect("prepare", self._on_drag_prepare)

    def remove_all(self):
        self._menu.unparent()
        super().remove_all()

    def _open_menu(self, row, x, y):
        self._menu.unparent()
        self._menu.set_parent(row)
        point=Graphene.Point.zero()
        point.x,point.y=x,y
        computed_point,point=self.compute_point(row, point)
        if computed_point:
            self._menu.open(row.song["file"], point.x, point.y)

    def _on_row_activated(self, list_box, row):
        self._client.file_to_playlist(row.song["file"], "play")

    def _on_keynav_failed(self, list_box, direction):
        if (root:=list_box.get_root()) is not None and direction == Gtk.DirectionType.UP:
            root.child_focus(Gtk.DirectionType.TAB_BACKWARD)

    def _on_button_pressed(self, controller, n_press, x, y):
        if (row:=self.get_row_at_y(y)) is not None:
            if controller.get_current_button() == 2 and n_press == 1:
                self._client.file_to_playlist(row.song["file"], "append")
            elif controller.get_current_button() == 3 and n_press == 1:
                self._open_menu(row, x, y)

    def _on_long_pressed(self, controller, x, y):
        if (row:=self.get_row_at_y(y)) is not None:
            self._open_menu(row, x, y)

    def _on_menu(self, action, state):
        row=self.get_focus_child()
        self._menu.unparent()
        self._menu.set_parent(row)
        self._menu.open(row.song["file"], 0, 0)

    def _on_drag_prepare(self, drag_source, x, y):
        if (row:=self.get_row_at_y(y)) is not None:
            return Gdk.ContentProvider.new_for_value(row.song)