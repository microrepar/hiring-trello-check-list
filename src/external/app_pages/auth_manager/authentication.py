"""Authentication
"""
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth # pip install streamlit-authenticator
import yaml
from yaml.loader import SafeLoader

from src.adapters import Controller


class MyAuth(stauth.Authenticate):
    def login(self, form_name: str, location: str='main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered, 
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if not st.session_state['authentication_status']:
            self._check_cookie()
            if not st.session_state['authentication_status']:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                login_form.subheader(form_name)
                self.username = login_form.text_input('Username').lower()
                try:
                    st.session_state['username'] = self.username.strip()
                except:
                    st.session_state['username'] = self.username

                self.password = login_form.text_input('Password', type='password')

                if login_form.form_submit_button('Login'):
                    self._check_credentials()

        return st.session_state['name'], st.session_state['authentication_status'], st.session_state['username']

    def register_user(self, form_name: str, location: str='main', preauthorization=True) -> bool:
        """
        Creates a register new user widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the register new user form.
        location: str
            The location of the register new user form i.e. main or sidebar.
        preauthorization: bool
            The preauthorization requirement, True: user must be preauthorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if preauthorization:
            if not self.preauthorized:
                raise ValueError("preauthorization argument must not be None")
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        new_email = register_user_form.text_input('Email')
        new_username = register_user_form.text_input('Username').lower()
        new_name = register_user_form.text_input('Name')
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        if register_user_form.form_submit_button('Register', use_container_width=False, type='primary'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials['usernames']:
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_email in self.preauthorized['emails']:
                                self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                                return True
                            else:
                                raise Exception('User not preauthorized to register')
                        else:
                            self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                            return True
                    else:
                        raise Exception('Passwords do not match')
                else:
                    raise Exception('Username already taken')
            else:
                raise Exception('Please enter an email, username, name, and password')
    


def streamlit_auth(placeholder_msg):

    if "user_dict" not in st.session_state:
        st.session_state.user_dict = {}

    config_file = Path(__file__).parent / "config.yaml"
    with config_file.open("rb") as file:
        config = yaml.load(file, Loader=SafeLoader)

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request = {"resource": "/user"}
    resp = controller(request=request)
    #############################################################
    messages = resp["messages"]
    entities = resp["entities"]
    #############################################################

    credentials = {"usernames": {}}
    user_dict = {}
    if not messages:
        for user in entities:
            credentials["usernames"].setdefault(user.username, {})
            credentials["usernames"][user.username]["name"] = user.name
            credentials["usernames"][user.username]["email"] = user.email
            credentials["usernames"][user.username]["password"] = user.password
            user_dict[user.username] = user
    else:
        placeholder_msg.warning("\n\n".join(messages))

    config["credentials"] = credentials
    st.session_state.credentials = credentials

    authenticator = MyAuth(
        config[
            "credentials"
        ],  # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
        config["cookie"]["name"],  # cookie:           str
        config["cookie"]["key"],  # cookie:           str
        config["cookie"]["expiry_days"],  # cookie:           str
        config["preauthorized"],  # preauthorized:    List[str]
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    return name, authentication_status, username, authenticator, credentials, user_dict
