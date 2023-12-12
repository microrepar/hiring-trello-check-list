
import datetime
from typing import List
from src.core.shared.entity import Entity
from src.core.candidate import Candidate


class Convocation(Entity):

    def __init__(self, 
                 id_        : int = None,
                 created_at : datetime.date = None,
                 updated_at : datetime.datetime = None,
                 created_by : int = None,
                 candidates : List[Candidate] = None,
                 ):
        super().__init__(id_, created_at, updated_at)

        self.created_by = created_by
        self.candidates = candidates