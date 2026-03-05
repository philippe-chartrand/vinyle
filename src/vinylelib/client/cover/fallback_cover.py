import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk


FALLBACK_COVER = Gdk.Paintable.new_empty(1, 1)