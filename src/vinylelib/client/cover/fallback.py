import gi
gi.require_version("Gtk", "4.0")
from .fallback_cover import FALLBACK_COVER


class FallbackCover(object):
    def get_paintable(self):
        return FALLBACK_COVER

