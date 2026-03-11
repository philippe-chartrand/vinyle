from .role import Role
from ..models import SelectionModel


class RoleSelectionModel(SelectionModel):
    def __init__(self):
        super().__init__(Role)
