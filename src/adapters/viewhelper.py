"""[summary]
"""
import abc
import datetime
import inspect
from collections import OrderedDict
from enum import Enum
from typing import Any, Dict, List

from src.core.shared.application import Result
from src.core.shared.entity import Entity
from src.core.shared.utils import string_to_date

primitive_types = [int, float, str, bool, bytes, datetime.date, dict, set] + Enum.__subclasses__()

class AbstractViewHelper(abc.ABC):
    @abc.abstractmethod
    def get_entities(self, *args: List[Entity], request: dict):
        """Receives a request and returns an instance of the object with the data filled in
        """

    @abc.abstractmethod
    def set_view(self, result: Result, request: dict):
        """Receives the request result object and prepares it to present in the view to the client
        """


#########################Implementation############################

class GenericViewHelper(AbstractViewHelper):

    def get_entities(self, *args: List[Entity], request: dict):

        domain_entities: List[Entity] = []

        # Iterates the list of classes to fill them with the request data
        for cls in args:

            # Retrieves the name of the class to use in retrieving request data
            class_name = cls.__name__.lower()

            entity_signature = inspect.signature(cls)

            kwargs = OrderedDict()
            for name, param in entity_signature.parameters.items():

                param_value = request.get(f'{class_name}_{name}')
                if param_value is None: continue

                if param.annotation in primitive_types:
                    if param.annotation in (datetime.date, ):
                        # TODO: create a function to prepare date value 
                        if param.annotation == type(param_value):
                            kwargs[name] = param_value
                        elif type(param_value) == str:
                            kwargs[name] = string_to_date(param_value)
                    else:
                        kwargs[name] = param.annotation(param_value)
                
                elif getattr(param.annotation, '__base__', None) == Entity:
                    inner_class_param = [param.annotation]
                    inner_value: List[Dict[str: Any]] = request.get(f'{class_name}_{name}')                    
                    kwargs[name] : List[Entity] = self.get_entities(*inner_class_param, request=inner_value)[-1]

                elif hasattr(param.annotation, '__origin__') \
                        and param.annotation.__origin__ is list:                    
                    if len(param.annotation.__args__) == 1 \
                            and getattr(param.annotation.__args__[0], '__base__', None) == Entity:
                        
                        inner_cls = param.annotation.__args__[0]
                        inner_class_param = [inner_cls]                        
                        values: List[Dict[str: Any]] = request.get(f'{class_name}_{name}')

                        if values:
                            attr_list = []
                            for inner_value in values:
                                attr_list.append(
                                    self.get_entities(*inner_class_param, request=inner_value)[-1]
                                )                
                            kwargs[name] = attr_list

                    else:
                        kwargs[name] = param_value
             
            entity = cls(**kwargs)

            domain_entities.append(entity)

        return domain_entities
    

    def set_view(self, result: Result, request):
        return result.to_dict()