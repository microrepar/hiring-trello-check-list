"""_summary_
adapted by: https://github.com/programadorLhama/CleanArch/blob/master/src/infra/db/settings/connection.py
"""
import os
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from config import Config


class DBConnectionHandler:

    def __init__(self) -> None:
        self._connection_string = Config.DATABASE_URL
        self._engine = self._create_database_engine()
        self._get_section()

    def _create_database_engine(self):
        engine = create_engine(self._connection_string)
        return engine

    def get_engine(self):
        return self._engine 

    def _get_section(self):
        session_make = sessionmaker(bind=self._engine)
        self.session = session_make()

    def close(self):
        self.session.close()