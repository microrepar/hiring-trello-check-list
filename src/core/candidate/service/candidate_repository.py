
import abc
from typing import Protocol, runtime_checkable

from src.core.shared.repository import Repository


@runtime_checkable
class CandidateRepository(Repository, Protocol):...
    