import datetime

from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/registry')
class UserRegistry(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        if not isinstance(entity, User):
            result.error_msg = f'{entity.__class__.__name__} is not a User Entity.'

        entity.status = 'active'

        result.error_msg = entity.validate_data()

        if result.qty_msg():
            result.entities = entity
            return result

        try:
            new_user = self.repository.registry(entity)
            result.entities = new_user
            return result
        except Exception as error:
            if 'user_email_key' in str(error) or 'failed: user.email' in str(error):
                result.error_msg = f'You cannot regtry email={entity.email} because it already exists.'
            elif 'user_username_key' in str(error) or 'user.username' in str(error):
                result.error_msg = f'You cannot regtry username={entity.username} because it already exists.'
            else:
                result.error_msg = str(error)
            
            result.entities = entity
            return result
