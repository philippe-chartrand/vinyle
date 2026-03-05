import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from gettext import gettext as _


class PlayButton(Gtk.Button):
    def __init__(self, client):
        super().__init__(icon_name="media-playback-start-symbolic", action_name="app.toggle-play", tooltip_text=_("Play"))
        client.emitter.connect("state", self._on_state)

    def _on_state(self, emitter, state):
        if state == "play":
            self.set_property("icon-name", "media-playback-pause-symbolic")
            self.set_tooltip_text(_("Pause"))
        else:
            self.set_property("icon-name", "media-playback-start-symbolic")
            self.set_tooltip_text(_("Play"))
