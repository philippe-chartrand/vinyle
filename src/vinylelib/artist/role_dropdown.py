import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class RoleDropDown(Gtk.DropDown):
    def __init__(self, values, initial_value):
        super().__init__()
        self.items = Gtk.StringList()
        self.props.model = self.items
        for item in values:
                self.items.append(item)
        self.set_selected_by_position(initial_value)
        self.props.selected

    def set_selected_by_position(self, new_value):
        if new_value is None:
            self.set_selected(0)
            return
        for no, known_role in enumerate(self.items):
            if new_value == known_role.props.string:
                self.set_selected(no)