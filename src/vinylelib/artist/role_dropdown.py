import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class RoleDropDown(Gtk.DropDown):
    def __init__(self, values, initial_value):
        super().__init__()
        self.values = values
        self.items = Gtk.StringList()
        self.props.model = self.items
        for item in self.values:
            self.items.append(item[1])
        self.set_selected_by_position(initial_value)
        self.props.selected


    def set_selected_by_position(self, new_value):
        if new_value is None:
            self.set_selected(0)
            return
        for no, known_role in enumerate(self.items):
            if self.values[no][0] == new_value and self.values[no][1] == known_role.props.string:
                self.set_selected(no)

    def get_selected(self):
        return self.values[self.props.selected][0]