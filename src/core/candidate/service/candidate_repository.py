
import abc
from typing import Any, Dict, List, Protocol, runtime_checkable
from src.core.candidate import Candidate

from src.core.shared.repository import Repository


@runtime_checkable
class CandidateRepository(Repository, Protocol):

    @abc.abstractclassmethod    
    def insert_label(self, entity: Candidate) -> Dict[str, Any]:
        """_summary_
        """

    @abc.abstractclassmethod
    def get_all_labels(self) -> List[Dict[str, Any]]:
        """_summary_
        """

    