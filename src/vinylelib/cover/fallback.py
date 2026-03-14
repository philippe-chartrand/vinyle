import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk

class FallbackCover(object):
    FALLBACK_COVER = Gdk.Paintable.new_empty(1, 1)

    def get_paintable(self):
        return self.FALLBACK_COVER

