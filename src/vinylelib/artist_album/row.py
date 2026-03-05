import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk


class ArtistAlbumRow(Adw.ActionRow):
    def __init__(self, album):
        super().__init__(use_markup=False, activatable=True, css_classes=["property"])
        self.album = album["album"]
        self.albumartist = album["albumartist"]
        self.date = album.get("date", "")
        # the next fields are optional, they are used to set the sidebar and the role dropdown at the right position when the user asks to show the album from the playlist
        self.artist = album.get("artist", "")
        self.composer = album.get("composer", "")
        self.conductor = album.get("conductor", "")
        self.performer = album.get("performer", "")

        # fill
        self.set_title(self.albumartist)
        self.set_subtitle(self.album)
        date = Gtk.Label(xalign=1, single_line_mode=True, css_classes=["numeric", "dimmed"])
        date.set_text(self.date)

        # packing
        self.add_suffix(date)
        self.add_suffix(
            Gtk.Image(icon_name="go-next-symbolic", accessible_role=Gtk.AccessibleRole.PRESENTATION))