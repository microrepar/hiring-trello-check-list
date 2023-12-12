"""Auth Manager main page
"""
import streamlit as st
from st_pages import add_page_title

from src.external.app_pages.auth_manager.authentication import streamlit_auth

st.set_page_config(layout='wide')


def on_click_btn_pages(*args, **kwargs):
    if kwargs.get('btn') == 'signup':
        st.session_state.btn_signup_page = True
        st.session_state.btn_reset_password_page = False

    elif kwargs.get('btn') == 'reset_password':
        st.session_state.btn_reset_password_page = True
        st.session_state.btn_signup_page = False
    else:
        st.session_state.btn_reset_password_page = False
        st.session_state.btn_signup_page = False

# ----- LOGIN MAIN ------
placeholder_msg = st.empty()

name, authentication_status, username, authenticator, credentials, user_dict = streamlit_auth(placeholder_msg)

add_page_title(layout='wide')


if 'btn_signup_page' not in st.session_state:
    if username == 'admin':
        st.session_state.btn_signup_page = True
    else:
        st.session_state.btn_signup_page = False

if 'btn_reset_password_page' not in st.session_state:
    if username == 'admin':
        st.session_state.btn_reset_password_page = False
    else:
        st.session_state.btn_reset_password_page = True

# Check login
if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:    
    # ---- LOGOUT SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    # ----------Sidebar Buttons----------
    if username == 'admin':        
        st.sidebar.button('Reset Password', 
                        type='primary' if st.session_state.btn_reset_password_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'reset_password'},
                        use_container_width=True)
        
        st.sidebar.button('Sign Up', 
                        type='primary' if st.session_state.btn_signup_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'signup'},
                        use_container_width=True)
    else:
        st.sidebar.button('Reset Password', 
                        type='primary' if st.session_state.btn_reset_password_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'reset_password'},
                        use_container_width=True)
        
    if st.session_state.btn_signup_page:
        from src.external.app_pages.auth_manager.signup import signup_page
        signup_page(authenticator, credentials, username)

    if st.session_state.btn_reset_password_page:
        from src.external.app_pages.auth_manager.reset_password \
            import reset_password_page
        reset_password_page(authenticator, credentials, username, placeholder_msg)
else:    
    st.session_state.pop('btn_signup_page')
    st.session_state.pop('btn_reset_password_page')
        