import gi
from gettext import gettext as _
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class CacheSizeDropDown(Gtk.DropDown):
    VALUES = (
        ('200', "200 {}".format( _("covers"))),
        ('400', "400 {}".format( _("covers"))),
        ('800', "800 {}".format(_("covers"))),
        ('1600',  "1600 {}".format(_("covers")))
    )

    def __init__(self, initial_value):
        super().__init__()
        self.items = Gtk.StringList()
        self.props.model = self.items
        for item in self.VALUES:
            self.items.append(item[1])
        self.set_selected_by_position(initial_value)

    def set_selected_by_position(self, new_value):
        if new_value is None:
            self.set_selected(0)
            return
        for no, known_size in enumerate(self.items):
            if self.VALUES[no][0] == new_value and self.VALUES[no][1] == known_size.get_string():
                self.set_selected(no)

    def get_selected(self):
        return self.VALUES[self.props.selected][0]