from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/remove')
class UserRemove(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        user_filter = User(id_=entity.username)
        user_exists = self.repository.find_by_field(entity)
        
        if not user_exists:
            result.error_msg = f'The user "{entity.username}" does not exists'
            result.entities = entity
            return result
        else:
            user_exists = user_exists[-1]
        
        try:
            if self.repository.remove(user_exists):
                result.objects = True
                return result
            else:
                result.error_msg = f'The user "{entity.username}" has not been removed or does not exist.'
                result.entities = entity
                return result
        except Exception as error:
            result.error_msg = str(error)
            result.entities = entity
            return result

