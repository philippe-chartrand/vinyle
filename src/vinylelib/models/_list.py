from gi.repository import GObject, Gio


class ListModel(GObject.Object, Gio.ListModel):
    def __init__(self, item_type):
        super().__init__()
        self.data=[]
        self._item_type=item_type

    def do_get_item(self, position):
        try:
            return self.data[position]
        except IndexError:
            return None

    def do_get_item_type(self):
        return self._item_type

    def do_get_n_items(self):
        return len(self.data)

