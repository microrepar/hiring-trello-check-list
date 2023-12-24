from src.core import usecase_map
from src.core.candidate import CandidateRepository
from src.core.convocation import Convocation
from src.core.shared import UseCase
from src.core.shared.application import Result


@usecase_map('/convocation/get_edital_label_list')
class ConvocationGetEditalLabelList(UseCase):

    def __init__(self, repository: CandidateRepository):
        self.repository = repository

    def execute(self, entity: Convocation = None) -> Result:
        result = Result()

        try:
            json_response = self.repository.get_all_labels()

            edital_dict = {}
            for label_dict  in sorted(json_response, key=lambda x: x['name'].split('/')[-1]):
                if 'EDITAL' in label_dict.get('name', '').upper():
                    edital_dict.update(
                        {label_dict['name']: label_dict['id']}
                    )

            result.objects = [edital_dict]

        except Exception as error:
            result.warning_msg = (f'ConvocationGetEditalLabelList: " {error}')

        return result