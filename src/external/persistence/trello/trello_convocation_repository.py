from typing import Any, Dict, List

import requests

from config import Config
from src.core.shared.utils import date_to_string
from src.core.candidate import Candidate, CandidateRepository
from src.external.persistence import repository_map

DESC_TEMPLATE = """Edital:{0}
Classificação: {1}
Data convocação: {2}
Data prazo: {3}
Secretaria Solicitante: {4}
Lotação:
Lotação original:
Relotado:
###PIS/PASEP:
OBSERVAÇÕES:
============
"""


def date_due(str_date):
    dia, mes, ano = str_date.split('/')
    horas = 'T20:00:00.000Z'
    return '-'.join([ano, mes, dia]) + horas


@repository_map
class TrelloConvocationRepository(CandidateRepository):

    def __init__(self) -> None:
        self.url = "https://api.trello.com/1/cards"

        self.headers = headers = {
            "Accept": "application/json"
        }

        self.querystring = {
            "key": Config.KEY_TRELLO,
            "token": Config.TOKEN_TRELLO
        }

        self.enrollment_label = {
            "ED.05/2018"   : "5c65c40ea7f53a50182c455f",
            "ED.11/2015"   : "5c2bb9041730b87826021475",
            "ED.13/2017"   : "5c2bb9286bf506324f87bc95",
            "ED.14/2017"   : "5c2bbad8a0696d3fd3a4c849",
            "COMISSIONADO" : "5c2bcdc9e2f265503052db6a",
            "INDEFINIDO"   : "5c2e4bfdfb5eea3e30a402ac",
            "ED.01/2016"   : "5c2e5c6ee658a942af0d9ce5",
            "ED.01/2019"   : "5d27499b87d0be7c5431310c"
        }



    def registry(self, entity: Candidate) -> Dict[str, Any]:
        querystring = {}
        querystring.update(self.querystring)

        querystring['idList']         = "58984d5c14e5f235609476af",
        querystring['idCardSource']   = "5e8799209416236e120b2c70",
        querystring['keepFromSource'] = "all",
        querystring['name']           = ' - '.join([f'{entity.classification:0>3}', entity.office.upper(), entity.complete_name.upper()])
        querystring['desc']           = DESC_TEMPLATE.format(entity.enrollment.split('.')[-1],
                                                             entity.classification, 
                                                             entity.convocation_date.strftime('%d/%m/%Y'),
                                                             entity.deadline.strftime('%d/%m/%Y'),
                                                             entity.department)
        
        response = requests.request("POST", self.url, headers=self.headers, params=querystring)
        response.raise_for_status()

        json_response = response.json()

        return json_response
    
    def insert_label(self, entity: Candidate) -> Dict[str, Any]:
        url_card = f'{self.url}/{entity.card_id}/idLabels'

        querystring = {}
        querystring.update(self.querystring)
        
        querystring["value"]  = self.enrollment_label.get(entity.enrollment,
                                                          self.enrollment_label['INDEFINIDO'])
        
        response = requests.request("POST", url_card, headers=self.headers, params=querystring)
        response.raise_for_status()

        json_response = response.json()

        return json_response    
    
    def update(self, entity: Candidate) -> Candidate:
        url_card = f"{self.url}/{entity.card_id}"

        querystring = {}
        querystring.update(self.querystring)

        querystring['start'] = entity.convocation_date.strftime('%Y-%m-%d') + 'T21:00:00.000Z'
        querystring['due'] = entity.deadline.strftime('%Y-%m-%d') + 'T21:00:00.000Z'

        response = requests.request("PUT", url_card, headers=self.headers, params=querystring)
        response.raise_for_status()
        json_response = response.json()

        return json_response
    
    def remove(self, entity: Candidate) -> bool:
        url_card = f"{self.url}/{entity.card_id}"

        querystring = {}
        querystring.update(self.querystring)

        response = requests.request("DELETE", url_card, params=querystring)
        response.raise_for_status()

        return response.text
    
    def get_all(self, entity: Candidate) -> List[Candidate]:
        return super().get_all(entity)
    
    def get_by_id(self, entity: Candidate) -> Candidate:
        return super().get_by_id(entity)
    
    def find_by_field(self, entity: Candidate) -> List[Candidate]:
        return super().find_by_field(entity)