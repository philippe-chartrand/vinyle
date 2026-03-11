from ..album import Album


class RoleAlbum(Album):
    """
    Created when user chooses a name in the sidebar, or clicks on a search result,
    one for every album associated with the artist.
    Destroyed when a user changes his selection in the sidebar,
    selects another artist after a search, or chooses to show an album from the playlist
    """
    def __init__(self, artist, role, name, date):
        super().__init__(name, date)
        self.artist=artist
        self.role=role