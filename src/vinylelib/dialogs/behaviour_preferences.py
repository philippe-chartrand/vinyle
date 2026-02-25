import gi


gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio
from gettext import gettext as _

from ..artist import Artist, RoleDropDown


class BehaviorPreferences(Adw.PreferencesGroup):
    def __init__(self, settings):
        super().__init__(title=_("Behavior"))
        self._settings = settings
        toggle_data=(
            (_("Send _Notification on Title Change"), "send-notify", ""),
            (_("Stop _Playback on Quit"), "stop-on-quit", ""),
            (_("Support “_MPRIS”"), "mpris", _("Disable if “MPRIS” is supported by another client")),
        )
        choice_data=(
            (_("Default browsing mode, (after restart)"), "default-browsing-mode",
             _("Choose your favorite sidebar navigation")),
        )

        for title, key, subtitle in toggle_data:
            row=Adw.SwitchRow(title=title, subtitle=subtitle, use_underline=True)
            settings.bind(key, row, "active", Gio.SettingsBindFlags.DEFAULT)
            self.add(row)

        for title, key, subtitle in choice_data:
            row=Adw.ActionRow(title=title, subtitle=subtitle, use_underline=True)
            role_dropdown = RoleDropDown(Artist.ROLES, self._settings["default-browsing-mode"])
            row.add_suffix(role_dropdown)
            role_dropdown.connect("notify::selected-item", self.on_role_selected)
            self.add(row)

    def on_role_selected(self, dropdown, _pspec):
        if dropdown.props.selected_item is None:
            return
        old_value = self._settings["default-browsing-mode"]
        new_value = dropdown.props.selected_item.props.string
        if new_value is not None and new_value != old_value:
            dropdown.set_selected_by_position(new_value)
            self._settings["default-browsing-mode"] = new_value
            self._settings.apply()