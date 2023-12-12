"""Application's entry point
Project name: Hiring Trello Check List
Author: Maurício Costa Silva
Description: Criador de check list na aplicação trello para 
    acompanhamente da entrega de documentos das pessoas 
    convocadas para contratação do processo de concursos 
    públicos da Prefeitura de Mogi das Cruzes
"""
import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages

from src.external.app_pages.auth_manager.authentication import streamlit_auth
from src.external.app_pages.candidate_list_page import candidate_list_page


st.set_page_config(layout='wide')

placeholder_msg = st.empty()

# -------------------------Authentication-------------------------
name, authentication_status, username, authenticator, credentials, user_dict = streamlit_auth(placeholder_msg)

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
    
    if username == 'admin':
        show_pages(
            [   
                Page("streamlit_app.py", "CHECKLIST TRELLO", "✅"),
                Page("src/external/app_pages/auth_manager/auth_manager_page.py", "Authentication Manager", "🔑"),
            ]
        )
    else:
        show_pages(
            [
                Page("streamlit_app.py", "CHECKLIST TRELLO", "🗂️"),
                Page("src/external/app_pages/auth_manager/auth_manager_page.py", "Authentication Manager", "🔑"),
            ]
        )
    
    add_page_title(layout='wide')
    candidate_list_page(username, user_dict)

else:    
    show_pages([Page("streamlit_app.py", "CHECKLIST TRELLO", "🗂️"),])