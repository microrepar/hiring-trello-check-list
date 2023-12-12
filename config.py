import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

FRAMEWORK_NAME = os.getenv('FRAMEWORK_NAME')

class Config:
    if FRAMEWORK_NAME == 'streamlit':
        import streamlit as st
        DATABASE_URL = st.secrets.get('DATABASE_URL')
        DB_DATABASE  = st.secrets.get('DB_DATABASE')
        DB_DIALECT   = st.secrets.get('DB_DIALECT')
        DB_HOST      = st.secrets.get('DB_HOST')
        DB_PASSWORD  = st.secrets.get('DB_PASSWORD')
        DB_PORT      = st.secrets.get('DB_PORT')
        DB_SCHEMA    = st.secrets.get('DB_SCHEMA')
        DB_USER      = st.secrets.get('DB_USER')
        
        REDIS_HOST         = st.secrets.get('REDIS_HOST')
        REDIS_PORT         = st.secrets.get('REDIS_PORT')
        REDIS_PASSWORD     = st.secrets.get('REDIS_PASSWORD')

        DB_FRAMEWORK = st.secrets.get('DB_FRAMEWORK')

    else:
        DATABASE_URL = os.getenv('DATABASE_URL')
        DB_DATABASE  = os.getenv('DB_DATABASE')
        DB_DIALECT   = os.getenv('DB_DIALECT')
        DB_HOST      = os.getenv('DB_HOST')
        DB_PASSWORD  = os.getenv('DB_PASSWORD')
        DB_PORT      = os.getenv('DB_PORT')
        DB_SCHEMA    = os.getenv('DB_SCHEMA')
        DB_USER      = os.getenv('DB_USER')

        REDIS_HOST         = os.getenv('REDIS_HOST')
        REDIS_PORT         = os.getenv('REDIS_PORT')
        REDIS_PASSWORD     = os.getenv('REDIS_PASSWORD')

        DB_FRAMEWORK = os.getenv('DB_FRAMEWORK')

    if DATABASE_URL is None:
        if DB_DIALECT and DB_DIALECT in 'postgresql mysql':
            DATABASE_URL = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"    
        else:
            DATABASE_URL = f"sqlite:///{Path(__file__).parent}/app.db"
