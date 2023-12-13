
import datetime
from typing import List
from src.core.shared.entity import Entity
from src.core.candidate import Candidate


class Convocation(Entity):

    def __init__(self, 
                 id_        : int = None,
                 created_at : datetime.date = None,
                 updated_at : datetime.datetime = None,
                 created_by : str = None,
                 candidates : List[Candidate] = None,
                 ):
        super().__init__(id_, created_at, updated_at)

        self.created_by = created_by
        self.candidates = candidates

    def validate_data(self) -> List[str]:
        messages = []

        for candidate in self.candidates:
            msg_list = candidate.validate_data()
            if msg_list:
                messages += msg_list
        
        if len(messages) != 0:
            messages.insert(0, '**Erro de preenchimento:** Os registros apresentaram os seguintes problemas.')

        return messages