import getpass
import sys

import streamlit as st
import streamlit_authenticator as stauth

from config import Config
from src.adapters import Controller


def create_user(*args):
    if len(args) == 4:
        name, username, email, password = args
        print(f'***CREATE USER {username}***')

    elif len(args) > 0 and args[-1] == 'admin':
        name     = 'codigo100cera'
        username = 'admin'
        email    = 'codigo100cera@gmail.com'
        password = 'ma180597'
        print(f'***CREATE USER {username}***')

    else:
        print('***CREATE USER***')
        name     = input('name (add your name): ')
        username = input('username: ')
        email    = input('email: ')
        password = getpass.getpass()    

    hashed_passwords = stauth.Hasher([password]).generate()

    #############################################################
    ### REGISTRY USER ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user/registry',
                    'user_username' : username.lower(),
                    'user_email'    : email.lower(),
                    'user_name'     : name,
                    'user_password' : hashed_passwords[-1],
                }

    resp       = controller(request=request)

    messages = resp['messages']
    entities = resp['entities']

    if messages:
        raise Exception('\n\n'.join(messages))

    print(f'User {username} created successfully.')
    #############################################################

    if len(args) != 4:
        exit()

if __name__ == '__main__':

    for line in sys.stdin:
        line = line.rstrip()        
        create_user(*line.split())