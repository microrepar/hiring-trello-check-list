from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.shared.repository import Repository
from src.core.user import User


@runtime_checkable
class UserRepository(Repository, Protocol):...