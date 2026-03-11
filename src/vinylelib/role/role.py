import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GObject
from gettext import gettext as _


class Role(GObject.Object):
    """
    Created when the sidebar list is populated, one for every name in the list provided by mpd
    """
    ROLES=(
        ('albumartist',_("Albumartist")),
        ('artist', _("Artist")),
        ('composer', _("Composer")),
        ('conductor', _("Conductor")),
        ('performer', _("Performer")),
        ('album', _("Album")),
        ('genre', _("Genre")),
        ('date', _("Year"))
    )

    def __init__(self, name, sort_key, role):
        GObject.Object.__init__(self)
        self.name=name
        self.sort_key=sort_key
        self.role=role