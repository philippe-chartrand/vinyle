import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio
from gettext import gettext as _

from ..widgets import CoverSizeDropDown


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

        covers_row = Adw.SpinRow.new_with_range(3, 8, 1)
        covers_row.set_title(_("Covers per row"))
        covers_row.set_subtitle(_("Requires a restart"))
        settings.bind("albums-page-columns", covers_row, "value", Gio.SettingsBindFlags.DEFAULT)
        self.add(covers_row)

        cover_row = Adw.ActionRow(title=_("Album cover size"), subtitle=_("Requires a restart"))
        cover_size_dropdown =  CoverSizeDropDown(settings["album-cover-size"])
        cover_row.add_suffix(cover_size_dropdown)
        self._settings = settings
        cover_size_dropdown.connect("notify::selected-item", self.on_cover_size_selected)
        self.add(cover_row)

    def on_cover_size_selected(self, dropdown, _pspec):
        if dropdown.props.selected_item is None:
            return
        old_value = self._settings["album-cover-size"]
        new_value = dropdown.get_selected()
        if new_value is not None and new_value != old_value:
            dropdown.set_selected_by_position(new_value)
            self._settings["album-cover-size"] = new_value
            self._settings.apply()