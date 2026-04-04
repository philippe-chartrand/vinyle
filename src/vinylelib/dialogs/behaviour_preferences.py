import gi


gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio
from gettext import gettext as _

from ..role import Role
from ..widgets import CacheSizeDropDown, RoleDropDown


class BehaviorPreferences(Adw.PreferencesGroup):
    def __init__(self, settings):
        super().__init__(title=_("Behavior"))
        self._settings = settings
        toggle_data=(
            (_("Send _Notification on Title Change"), "send-notify", ""),
            (_("Stop _Playback on Quit"), "stop-on-quit", ""),
            (_("Support “_MPRIS”"), "mpris", _("Disable if “MPRIS” is supported by another client")),
            (_("Log to playlist"), "log-to-playlist",_("Register played songs in a dedicated playlist"))
        )
        choice_data=(
            (_("Default browsing mode, (after restart)"), "default-browsing-mode",
             _("Choose your favorite sidebar navigation")),
        )
        cache_size_data = (
            (_("Size of the cover cache, (change effective after restart)"), "cover-cache-size",
             _("Depending on the collection size and the available computer memory")),
        )

        for title, key, subtitle in toggle_data:
            row=Adw.SwitchRow(title=title, subtitle=subtitle, use_underline=True)
            settings.bind(key, row, "active", Gio.SettingsBindFlags.DEFAULT)
            self.add(row)

        for title, key, subtitle in choice_data:
            row=Adw.ActionRow(title=title, subtitle=subtitle, use_underline=True)
            role_dropdown = RoleDropDown(Role.ROLES, self._settings[key])
            row.add_suffix(role_dropdown)
            role_dropdown.connect("notify::selected-item", self.on_role_selected)
            self.add(row)

        for title, key, subtitle in cache_size_data:
            row = Adw.ActionRow(title=title, subtitle=subtitle, use_underline=True)
            cache_size_dropdown = CacheSizeDropDown(self._settings[key])
            row.add_suffix(cache_size_dropdown)
            cache_size_dropdown.connect("notify::selected-item", self.on_cache_size_selected)
            self.add(row)

        max_albums_row = Adw.SpinRow.new_with_range(100, 1000, 100)
        max_albums_row.set_title(_("Maximum albums per page"))
        max_albums_row.set_subtitle(_("Requires a restart"))
        settings.bind("max-number-of-albums", max_albums_row, "value", Gio.SettingsBindFlags.DEFAULT)
        self.add(max_albums_row)

        max_items_row = Adw.SpinRow.new_with_range(200, 2000, 200)
        max_items_row.set_title(_("Maximum number of items from a playlist"))
        max_items_row.set_subtitle(_("Requires a restart"))
        settings.bind("max-number-of-playlist-items", max_items_row, "value", Gio.SettingsBindFlags.DEFAULT)
        self.add(max_items_row)

    def on_role_selected(self, dropdown, _pspec):
        if dropdown.props.selected_item is None:
            return
        old_value = self._settings["default-browsing-mode"]
        new_value = dropdown.get_selected()
        if new_value is not None and new_value != old_value:
            dropdown.set_selected_by_position(new_value)
            self._settings["default-browsing-mode"] = new_value
            self._settings.apply()

    def on_cache_size_selected(self, dropdown, _pspec):
        if dropdown.props.selected_item is None:
            return
        old_value = self._settings["cover-cache-size"]
        new_value = dropdown.get_selected()
        if new_value is not None and new_value != old_value:
            dropdown.set_selected_by_position(new_value)
            self._settings["cover-cache-size"] = new_value
            self._settings.apply()