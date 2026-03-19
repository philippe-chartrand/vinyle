import datetime
import logging
from gi.repository import Gtk, GObject
import locale
from ._list import ListModel


class SelectionModel(ListModel, Gtk.SelectionModel):
    """
    Used to represent a list of objects that is selectable,
    such as an artist name in the sidebar, a selection of albums for a given artist,
    a song in the playlist, or an album in the artist albums page.
    An item in the collection is identified by his index.
    """
    __gsignals__={"selected": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
            "reselected": (GObject.SignalFlags.RUN_FIRST, None, ()),
            "clear": (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self, item_type, log=False):
        super().__init__(item_type)
        self._selected=None
        self.log = True
        self.logger = logging.getLogger(__name__)

    def _log_debug(self, message):
        if self.log:
            self.logger.debug("%s, %s, class:%s, size:%s", datetime.datetime.now(), message,
                              str(self._item_type), len(self.data))

    def _log_info(self, message):
        if self.log:
            self.logger.info("%s, %s, class:%s, size:%s", datetime.datetime.now(), message,
                              str(self._item_type), len(self.data))

    def clear(self, position=0):
        self._log_debug('items before clear')
        n=self.get_n_items()-position
        self.data=self.data[:position]
        if self._selected is not None:
            if self._selected >= self.get_n_items():
                self._selected=None
        self.items_changed(position, n, 0)
        self._log_debug('items after clear')
        if position == 0:
            self.emit("clear")

    def append(self, data):
        n=self.get_n_items()
        self.data.extend(data)
        self._log_info('appending')
        self.items_changed(n, 0, self.get_n_items())

    def get_selected(self):
        return self._selected

    def set(self, position, item):
        if position < len(self.data):
            self.data[position]=item
            self.items_changed(position, 1, 1)
        else:
            self.data.append(item)
            self.items_changed(position, 0, 1)

    def select(self, position):
        if position == self._selected:
            self.emit("reselected")
        else:
            old_selected=self._selected
            self._selected=position
            if old_selected is not None:
                self.selection_changed(old_selected, 1)
            self.selection_changed(position, 1)
            self.emit("selected", position)

    def unselect(self):
        old_selected=self._selected
        self._selected=None
        if old_selected is not None:
            self.selection_changed(old_selected, 1)

    def do_select_item(self, position, unselect_rest): return False
    def do_select_all(self): return False
    def do_select_range(self, position, n_items, unselect_rest): return False
    def do_set_selection(self, selected, mask): return False
    def do_unselect_all(self): return False
    def do_unselect_item(self, position): return False
    def do_unselect_range(self, position, n_items): return False
    def do_get_selection_in_range(self, position, n_items): return False

    def do_is_selected(self, position):
        return position == self._selected

    def set_list(self, items):
        self.clear()
        reverse = True if len(items) and items[0][2] == 'date' else False
        self.append((self.do_get_item_type()(item[0], item[1], item[2])
                     for item in sorted(items, key=lambda item: locale.strxfrm(item[1]), reverse=reverse)))

    def select_item(self, name):
        for i, item in enumerate(self.data):
            if item.name == name:
                self.select(i)
                return

    def get_item_name(self, position):
        return self.get_item(position).name

    def get_selected_item(self):
        if (selected:=self.get_selected()) is None:
            return None
        else:
            return self.get_item_name(selected)