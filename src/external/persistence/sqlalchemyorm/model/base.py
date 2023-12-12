import datetime
import json
from typing import List

from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, MetaData, Sequence, String, Table,
                        Text, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.core.user import User

# Base = declarative_base(metadata=MetaData(schema='<your_schema>'))
Base = declarative_base()
metadata = Base.metadata


class UserModel(Base):
    __tablename__  = 'user'
    # __table_args__ = {"schema": "<your_schema>"}

    id         = Column(Integer, primary_key=True)
    created_at = Column(Date, default=func.current_date())
    name       = Column(String)
    age        = Column(String)
    username   = Column(String)
    password   = Column(String)

    @classmethod
    def user_model_to_entity(cls, model: 'UserModel') -> User:
        return User(
            id_        = model.id,
            created_at = model.created_at,
            name       = model.name,
            age        = model.age,
            username   = model.username,
            password   = model.password
        )
    
    @classmethod
    def user_entity_to_model(cls, entity: User) -> 'UserModel':
        return cls(
            id         = entity.id,
            created_at = entity.created_at,
            name       = entity.name,
            age        = entity.age,
            username   = entity.username,
            password   = entity.password
        )