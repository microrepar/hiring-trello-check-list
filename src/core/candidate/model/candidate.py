
from src.core.shared.entity import Entity


class Candidate(Entity):

    def __init__(self, id_=None, created_at=None, updated_at=None):
        super().__init__(id_, created_at, updated_at)

    