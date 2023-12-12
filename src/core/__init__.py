"""core module
"""

import os
from importlib import import_module
from pathlib import Path
from typing import Generic

from .shared.application import Result
from .shared.usecase import I, T, UseCase


class UsecaseNotFoundError(UseCase):

    def __init__(self, repository: Generic[T]):
        self.execute(repository)
    
    def execute(self, entidade: Generic[I]=None) -> Result:
        result = Result()
        result.error_msg = 'Resource was not found.'
        return result


usecases = {'default': UsecaseNotFoundError}


def usecase_map(resource=None):
    def wrapper(cls):
        usecases.update({resource: cls})
        return cls
    return wrapper


here = Path(os.path.dirname(__file__))
for package in here.iterdir():
    if package.is_dir():
        for service in package.iterdir():
            if service.is_dir() and service.name == 'service':                
                for repository_module in service.iterdir():
                    if repository_module.name.endswith('.py') \
                            and not repository_module.name.startswith('_')\
                            and not repository_module.name.endswith('_repository.py'):

                        model_name = package.name
                        service_name = service.name
                        module_name = repository_module.name.split('.')[0]

                        module = import_module('src.core.{}.{}.{}'.format(model_name, service_name, module_name))
                        # print('src.core.{}.{}.{}'.format(model_name, service_name, module_name))
