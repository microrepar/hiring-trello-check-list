import abc
from typing import List, Protocol, runtime_checkable

from .entity import Entity


@runtime_checkable
class Repository(Protocol):
    
    @abc.abstractmethod
    def registry(self, entity: Entity) -> Entity:
        """Registry a entity into database
        """

    @abc.abstractmethod
    def get_all(self, entity: Entity) -> List[Entity]:
        """Get all registred entity in database
        """

    @abc.abstractmethod
    def update(self, entity: Entity) -> Entity:
        """Updates the values ​​of entity fields in the database
        """
    
    @abc.abstractmethod
    def find_by_field(self, entity: Entity) -> List[Entity]:
        """Find entity from database by field
        """
    
    @abc.abstractmethod
    def get_by_id(self, entity: Entity) -> Entity:
        """Locate the entity registered in the database using the field
        """
    
    @abc.abstractmethod
    def remove(self, entity: Entity) -> bool:
        """Remove entity from database by id
        """

