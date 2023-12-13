import datetime

from src.core import usecase_map
from src.core.candidate import CandidateRepository
from src.core.convocation import Convocation
from src.core.shared import UseCase
from src.core.shared.application import Result


@usecase_map('/convocation/create_checklist')
class ConvocationCreateChecklist(UseCase):

    def __init__(self, repository: CandidateRepository):
        self.repository = repository

    def execute(self, entity: Convocation) -> Result:
        result = Result()

        print('>>>>>>>>>>>>>>>>>', entity.candidates)
        result.error_msg = entity.validate_data()
        if result.qty_msg():
            return result
        
        candidate_checklist_error_list = []

        contador = 0
        for candidate in entity.candidates:

            candidate.created_at = datetime.datetime.now().date()

            try:
                json_response = self.repository.registry(candidate)
                candidate.card_id = json_response['id']
            except Exception as error:
                result.warning_msg = (
                    f'ConvocationCreateChecklistWarning: candidate name "{candidate.complete_name}" {error}')
                candidate_checklist_error_list.append(candidate)
                continue
            else:
                contador += 1                
            
            try:
                self.repository.insert_label(candidate)
            except Exception as error:
                result.warning_msg = (f'ConvocationCreateChecklistWarnning: '
                                      f'ocorreu um erro ao inserir a label {candidate.enrollment} '
                                      f'para o edital "{candidate.enrollment}" - {error}')
        if contador > 0:
            result.success_msg = f'Foram criados {contador} checklist(s) no Trello.'
        
        if candidate_checklist_error_list:
            entity.candidates = candidate_checklist_error_list
            result.entities = entity
        
        return result