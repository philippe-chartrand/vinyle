import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio
from gettext import gettext as _


class ViewPreferences(Adw.PreferencesGroup):
    def __init__(self, settings):
        super().__init__(title=_("View"))
        toggle_data=(
            (_("_Show Bit Rate"), "show-bit-rate", ""),
        )
        for title, key, subtitle in toggle_data:
            row=Adw.SwitchRow(title=title, subtitle=subtitle, use_underline=True)
            settings.bind(key, row, "active", Gio.SettingsBindFlags.DEFAULT)
            self.add(row)

        row = Adw.SpinRow.new_with_range(3, 8, 1)
        row.set_title(_("Covers per row"))
        settings.bind("albums-page-columns", row, "value", Gio.SettingsBindFlags.DEFAULT)
        self.add(row)