import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib

from .fallback import FallbackCover

class BinaryCover(bytes):
    def get_paintable(self):
        try:
            paintable=Gdk.Texture.new_from_bytes(GLib.Bytes.new(self))
        except gi.repository.GLib.Error:  # load fallback if cover can't be loaded
            paintable=FallbackCover().get_paintable()
        return paintable