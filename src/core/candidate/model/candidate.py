
import datetime
from typing import List
from src.core.shared.utils import date_to_string
from src.core.shared.entity import Entity


class Candidate(Entity):

    def __init__(self, 
                 id_              : int =None,
                 created_at       : datetime.date =None,
                 updated_at       : datetime.datetime =None,
                 complete_name    : str = None,
                 enrollment       : str = None,
                 classification   : int = None,
                 office           : str = None,
                 convocation_date : datetime.date = None,
                 deadline         : datetime.date = None,
                 notice           : str = None,
                 department       : str = None,
                 card_id          : str=None
                 ):
        
        super().__init__(id_, created_at, updated_at)

        self.complete_name    = complete_name
        self.enrollment       = enrollment
        self.classification   = classification
        self.office           = office
        self.convocation_date = convocation_date
        self.deadline         = deadline
        self.notice           = notice
        self.department       = department
        self.card_id          = card_id

    def __repr__(self) -> str:
        return (
            f'Candidate('
            f'id_={self.id}, '
            f'created_at={self.created_at}, '
            f'updated_at={self.updated_at}, '
            f'complete_name={self.complete_name}, '
            f'enrollment={self.enrollment}, '
            f'classification={self.classification}, '
            f'office={self.office}, '
            f'convocation_date={self.convocation_date}, '
            f'deadline={self.deadline}, '
            f'notice={self.notice}, '
            f'department={self.department}, '
            f'card_id={self.card_id}'
            f')'
        )
    
    def data_to_dataframe(self):
        return [
            {
                'nome'       : self.complete_name,
                'insc'       : self.enrollment,
                'classif'    : self.classification,
                'cargo'      : self.office,
                'convocacao' : self.convocation_date,
                'prazo'      : self.deadline,
                'edital'     : self.notice,
                'secretaria' : self.department,
            }
        ]


    def validate_data(self) -> List[str]:
        messages = []
        
        attr_map = {
            'complete_name'    : 'nome',
            'enrollment'       : 'insc',
            'classification'   : 'classificação',
            'office'           : 'cargo',
            'convocation_date' : 'convocacao',
            'deadline'         : 'prazo',
            'notice'           : 'edital'
        }

        for attr in attr_map:
            value = getattr(self, attr, None)

            if value is None:
                messages.append(
                    f'\tO campo "{attr_map[attr]}" é obrigatório o preenchimento'
                )
            else:
                try:                
                    value = value.strip()                
                    setattr(self, attr, value)
                except:
                    pass

                value = date_to_string(value)
                if value == '' or value is None:
                    messages.append(
                        f'\tO campo "{attr_map[attr]}" é obrigatório o preenchimento'
                    )
        
        if len(messages) != 0:
            messages.insert(0, f'Candidato: {self.complete_name}')
        return messages
