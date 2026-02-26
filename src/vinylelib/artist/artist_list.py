import itertools
import gi
from gettext import gettext as _

from ..sidebar_list_view import SidebarListView

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Pango, GLib


class ArtistList(SidebarListView):
    def __init__(self, client, SelectionModel, artist_role):
        super().__init__(client, SelectionModel)
        self.artist_role = artist_role

    @staticmethod
    def move_initial_article(artist):
        moveable_articles = ('The ', 'Les ')
        if artist[0:4] in moveable_articles:
             return f"{artist[4:]}, {artist[0:2]}"
        else:
            return artist

    def refresh(self):
        # TODO: simplify me
        # grouping and iterator logic does not seem necessary
        artists = self._client.list(self.artist_role)
        artist_iterator = itertools.groupby( ((artist[self.artist_role]) for artist in artists ),
                                                key=lambda x: x)
        filtered_artists=[]
        for name, artist in artist_iterator:
            if name == "":
                next(artist)
                continue
            value = next(artist)
            artist_with_role= [value, self.move_initial_article(name), self.artist_role]
            filtered_artists.append(artist_with_role)
            # ignore multiple albumartistsort values
            if next(artist, None) is not None:
                filtered_artists[-1]=(name, name, self.artist_role)
        self.selection_model.set_list(filtered_artists)

    def _on_connected(self, emitter, database_is_empty):
        if not database_is_empty:
            self.refresh()
            if (song:=self._client.currentsong()):
                artist=song[self.artist_role][0]
                self.select(artist)