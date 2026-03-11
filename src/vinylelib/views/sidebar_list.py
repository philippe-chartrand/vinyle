import itertools
import gi
gi.require_version("Gtk", "4.0")

from .sidebar import SidebarListView


class SidebarList(SidebarListView):
    def __init__(self, client, SelectionModel, sidebar_role):
        super().__init__(client, SelectionModel)
        self.tag_name = sidebar_role

    @staticmethod
    def move_initial_article(item):
        moveable_articles = ('The ', 'Les ')
        if item[0:4] in moveable_articles:
             return f"{item[4:]}, {item[0:2]}"
        else:
            return item

    def _create_iterator_from_list(self, items):
        # expects a list of dicts where the key is the tag name, and the associated value for the tag
        # date tags are treated as years
        return itertools.groupby(
            ((item[self.tag_name][0:4] if self.tag_name == 'date' else item[self.tag_name]) for item in
             items),
            key=lambda x: x)

    def _filter_from_iterator(self, iterator):
        filtered_items = []
        for name, grouper in iterator:
            if name == "":
                next(grouper)
                continue
            value = next(grouper)
            value_with_sort_key_and_role = [value, self.move_initial_article(name), self.tag_name]
            filtered_items.append(value_with_sort_key_and_role)
            # ignore multiple albumartistsort values
            if next(grouper, None) is not None:
                filtered_items[-1] = (name, name, self.tag_name)
        return filtered_items

    def refresh(self):
        # TODO: grouping and iterator logic does not seem necessary
        items = self._client.list(self.tag_name)
        items_iterator = self._create_iterator_from_list(items)
        filtered_items = self._filter_from_iterator(items_iterator)
        self.selection_model.set_list(filtered_items)

    def _on_connected(self, emitter, database_is_empty):
        if not database_is_empty:
            self.refresh()
            if (song:=self._client.currentsong()):
                item=song[self.tag_name][0]
                self.select(item)