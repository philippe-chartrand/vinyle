import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject


class Artist(GObject.Object):
    ROLES=('albumartist','artist', 'composer', 'conductor', 'performer')
    def __init__(self, name, sort_key, role):
        GObject.Object.__init__(self)
        self.name=name
        self.sort_key=sort_key
        self.role=role
