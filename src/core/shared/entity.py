import abc
import datetime
from typing import List


class Entity(abc.ABC):

    def __init__(self, id_=None, created_at=None, updated_at=None):
        self.id         : int = id_
        self.created_at : datetime.datetime = created_at
        self.updated_at : datetime = updated_at

    @abc.abstractmethod
    def validate_data(self) -> List[str]:
        """_summary_
        """

