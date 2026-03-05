from .artist import Artist
from ..models import SelectionModel


class ArtistSelectionModel(SelectionModel):
    def __init__(self):
        super().__init__(Artist)
