from abc import abstractmethod
from typing import Generic, Protocol, TypeVar, runtime_checkable

from .application import Result

I = TypeVar('I')
T = TypeVar('T')


@runtime_checkable
class UseCase(Protocol):

    @abstractmethod
    def __init__(self, repository: Generic[T]):
        """Initial Interfave for usecases
        """

    @abstractmethod
    def execute(self, entity: Generic[I]) -> Result:
        """Generic Interface for usecases"""
