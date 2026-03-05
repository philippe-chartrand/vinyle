import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from gettext import gettext as _

from .play_button import PlayButton

class MediaButtons(Gtk.Box):
    def __init__(self, client):
        super().__init__(spacing=6)
        self.append(Gtk.Button(icon_name="media-skip-backward-symbolic", tooltip_text=_("Previous"), action_name="app.previous"))
        self.append(PlayButton(client))
        self.append(Gtk.Button(icon_name="media-skip-forward-symbolic", tooltip_text=_("Next"), action_name="app.next"))

