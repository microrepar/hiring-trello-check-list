"""application module
"""

from collections.abc import Sequence
from typing import Any, Iterable, List

from .entity import Entity

entity_list = List[Entity]
list_str = List[str]


class Result:

    def __init__(self):
        self._error_msg   : List[str] = list()
        self._info_msg    : List[str] = list()
        self._success_msg : List[str] = list()
        self._warnig_msg  : List[str] = list()
        self._entities    : List[str] = list()
        self._objects     : List[Any] = list()
        self.form = None

    @property
    def error_msg(self) -> list_str:
        return self._error_msg

    @error_msg.setter
    def error_msg(self, message: str):
        if isinstance(message, str):
            self._error_msg += list([message])
        elif isinstance(message, Sequence):
            self._error_msg += list(message)

    @property
    def warning_msg(self) -> list_str:
        return self._warnig_msg

    @warning_msg.setter
    def warning_msg(self, message: str):
        if isinstance(message, str):
            self._warnig_msg += list([message])
        elif isinstance(message, Sequence):
            self._warnig_msg += list(message)

    @property
    def info_msg(self) -> list_str:
        return self._info_msg

    @info_msg.setter
    def info_msg(self, message: str):
        if isinstance(message, str):
            self._info_msg += list([message])
        elif isinstance(message, Sequence):
            self._info_msg += list(message)

    @property
    def success_msg(self) -> list_str:
        return self._success_msg

    @success_msg.setter
    def success_msg(self, message: str):
        if isinstance(message, str):
            self._success_msg += list([message])
        elif isinstance(message, Sequence):
            self._success_msg += list(message)

    @property
    def objects(self) -> Any:
        return self._objects
    
    @objects.setter
    def objects(self, objs = List[Any]):
        if isinstance(objs, Iterable):
            self._objects += list(objs)
        else:
            self._objects += list([objs])
        
    @property
    def entities(self) -> entity_list:
        return self._entities

    @entities.setter
    def entities(self, entities: List[Entity]):
        if isinstance(entities, Entity):
            self._entities += list([entities])
        elif isinstance(entities, Sequence):
            for entity in entities:
                if not isinstance(entity, Entity):
                    raise Exception(f'This {entity} is not Entity.')
            self._entities += list(entities)

    def qty_entities(self):
        return len(self._entities)

    def qty_msg(self):
        return len(self._error_msg)
    
    def to_dict(self):
        return {
            'messages': self._error_msg,
            'entities': self._entities,
            'objects': self._objects,
        }