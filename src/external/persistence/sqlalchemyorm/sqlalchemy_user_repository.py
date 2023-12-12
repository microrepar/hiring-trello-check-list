from typing import List

from src.core.user import User, UserRepository
from src.external.persistence import repository_map

from .model.base import UserModel
from .settings.connection import DBConnectionHandler


@repository_map
class SlalchemyUserRepository(UserRepository):

    def __init__(self):
        self.database = DBConnectionHandler()
    
    def registry(self, entity: User) -> User:
        model = UserModel.user_entity_to_model(entity)
        try:
            with self.database.session.begin():
                self.database.session.add(model)
            
            new_entity = UserModel.user_model_to_entity(model)
            return new_entity
        
        except Exception as error:
            self.database.session.rollback()
            self.database.close()
            raise error

    def get_all(self, entity: User) -> List[User]:
        model_list = self.database.session.query(UserModel).all()

        entity_list = [UserModel.user_model_to_entity(m) for m in model_list]

        return entity_list
        
    def update(self, entity: User) -> User:
        raise Exception('"update method" in "SlalchemyUserRepository" is not implemented')
    
    def remove(self, entity: User) -> bool:
        raise Exception('"remove" method in "SlalchemyUserRepository" is not implemented')
