from gettext import gettext as _
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, GLib, Gtk, GObject, Pango

from .cover import AlbumCover
from ..browsersong import BrowserSongList


class AlbumPage(Adw.NavigationPage):
    def __init__(self, client, album, date):
        super().__init__()
        tag_filter=("album", album, "date", date)

        # songs list
        self.song_list=BrowserSongList(client)
        self.song_list.add_css_class("boxed-list")

        # buttons
        self.play_button = Gtk.Button(icon_name="arrow-right-symbolic", tooltip_text=_("Play selection"),  css_classes=["flat"])
        self.append_button = Gtk.Button(icon_name="list-add-symbolic", tooltip_text=_("Append selection"), css_classes=["flat"])
        self.play_all_button = Gtk.Button(icon_name="arrow-right-double-symbolic", tooltip_text=_("Play All"),  css_classes=["raised"])
        self.append_all_button = Gtk.Button(icon_name="list-add-double-symbolic", tooltip_text=_("Append All"), css_classes=[ "raised"])

        # header bar
        self.header_bar=Adw.HeaderBar(show_title=False)
        self.header_bar.pack_end(self.play_all_button)
        self.header_bar.pack_end(self.append_all_button)
        self.header_bar.pack_end(self.play_button)
        self.header_bar.pack_end(self.append_button)

        # labels
        self.suptitle=Gtk.Label(single_line_mode=True, ellipsize=Pango.EllipsizeMode.END, css_classes=["dimmed", "caption"])
        self.title=Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER, css_classes=["title-4"])
        self.subtitle=Gtk.Label(single_line_mode=True, ellipsize=Pango.EllipsizeMode.END, visible=bool(date))
        self.length=Gtk.Label(single_line_mode=True, css_classes=["numeric", "dimmed", "caption"])

        # label box
        label_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3, margin_top=9, margin_bottom=18)
        label_box.append(self.suptitle)
        label_box.append(self.title)
        label_box.append(self.subtitle)
        label_box.append(self.length)

        # cover
        self.album_cover=AlbumCover()

        # packing
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=12, margin_end=12, margin_top=6, margin_bottom=24)
        box.append(Adw.Clamp(child=self.album_cover, maximum_size=200))
        box.append(label_box)
        box.append(Adw.Clamp(child=self.song_list))
        self._scroll=Gtk.ScrolledWindow(child=box)
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view=Adw.ToolbarView(content=self._scroll)
        toolbar_view.add_top_bar(self.header_bar)
        self.set_child(toolbar_view)

        # populate
        if album:
            self.set_title(album)
            self.title.set_text(album)
        else:
            self.set_title(_("Unknown Album"))
            self.title.set_text(_("Unknown Album"))
        if date:
            self.subtitle.set_text(date[0:4])
        client.tagtypes("all")
