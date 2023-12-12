from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/update_detail')
class UserUpdateDetail(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        user_filter = User(username=entity.username)
        user_exists = self.repository.find_by_field(user_filter)
        
        if not user_exists:
            result.error_msg = f'Username={entity.username} no exists'
            result.entities = entity
            return result
        else:
            user_exists = user_exists[-1]
        
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])
        kwargs = {}
        for attr, value in filters.items():
            if attr in 'name email status username password':
                kwargs[attr] = value                

        if len(kwargs) == 0:
            result.error_msg = f'Field is empty.'
            result.entities = entity
            return result
        
        attr_list = list()
        count = 0
        for attr, value in kwargs.items():
            if getattr(user_exists, attr) != value:
                setattr(user_exists, attr, value)
            else:
                attr_list.append(attr)
                count += 1

        if count == len(kwargs):
            result.error_msg = f'New and current values to field={attr_list} are the same'
        
        try:
            updated_user = self.repository.update(user_exists)
            result.entities = updated_user
            return result
        except Exception as error:
            if 'user_email_key' in str(error):
                result.error_msg = f'You cannot update email={entity.email} because it already exists.'
            elif 'user_username_key' in str(error):
                result.error_msg = f'You cannot update username={entity.username} because it already exists.'
            else:
                result.error_msg = str(error)
            result.entities = entity
            return result
        ###################################