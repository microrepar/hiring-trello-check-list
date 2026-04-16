import pandas as pd
import streamlit as st  # pip install streamlit

from src.adapters import Controller


def signup_page(authenticator, credentials, username):

    set_usernames = set(credentials['usernames'])

    try:
        registry = authenticator.register_user('User register', preauthorization=False)

        if registry:
            #############################################################
            ### REGISTRY USER ###
            #############################################################
            new_username = (set(credentials['usernames']) - set_usernames).pop()
            print(new_username)
            controller = Controller()
            request = {
                'resource'      : '/user/registry',
                'user_username' : new_username,
                'user_email'    : credentials['usernames'][new_username]['email'],
                'user_name'     : credentials['usernames'][new_username]['name'],
                'user_password' : credentials['usernames'][new_username]['password'],
            }

            resp = controller(request=request)

            messages = resp['messages']
            entities = resp['entities']

            if 'error' in messages:
                raise Exception('\n\n'.join(messages['error']))
            #############################################################

            st.success('User registered successfully')

    except Exception as e:
        st.error(e)


    st.divider()
    st.markdown('### Resgistred Users')
    #############################################################
    ### GET ALL PLANNEDEVENT ###
    #############################################################
    controller = Controller()
    request = {'resource': '/user',
               'user_username': username,
               }
    resp = controller(request=request)
    #############################################################
    messages = resp.get('messages', [])
    entities = resp.get('entities', [])
    #############################################################
    if 'info' in messages:
        st.info('\n  - '.join(messages['info']), icon='ℹ️')
    if 'warning' in messages:
        st.warning('\n  - '.join(messages['warning']), icon='⚠️')
    if 'success' in messages:
        st.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################

    if 'error' in messages:
        st.error('\n  -'.join(messages['error']), icon='🚨')
    elif entities:
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)

        editor_config = {
            'name'     : st.column_config.TextColumn('Name (required)', required=True),
            'password' : st.column_config.TextColumn('Password', required=True),
            'username' : st.column_config.TextColumn('Username',  required=True),
            'email'    : st.column_config.TextColumn('E-mail (required)', required=True),
            'status'   : st.column_config.SelectboxColumn('Status', options=['active', 'removed', 'blocked'], required=True),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False

        disable_fields = ['id', 'created_at', 'updated_at', 'username']

        if st.session_state.flag_reset:
            editor_key = 'update_data1'
            form_key = 'user_form1'
        else:
            editor_key = 'update_data'
            form_key = 'user_form'

        placeholder_error = st.empty()
        placeholder_success = st.empty()
        placeholder_warning = st.empty()

        # Usar st.form para prevenir reruns automáticos do data_editor
        with st.form(form_key):
            edited_df = st.data_editor(df,
                                       num_rows="dynamic",
                                       column_config=editor_config,
                                       disabled=disable_fields,
                                       use_container_width=True,
                                       key=editor_key)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted_save = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type='primary')
            with col_btn2:
                submitted_cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

        # Processar submissão do formulário
        if submitted_save:
            error_messages = []
            success_messages = []
            warning_messages = []

            # Processar deleções
            if st.session_state[editor_key].get('deleted_rows'):
                username_list = []
                for index in st.session_state[editor_key]['deleted_rows']:
                    user_username = df.iloc[index]['username']

                    if user_username and 'admin' in user_username:
                        warning_messages.append('User "admin" cannot be removed')
                    else:
                        user_id = df.iloc[index]['id']
                        #############################################################
                        ### DELETE USER BY ID ###
                        #############################################################
                        controller = Controller()
                        request = {'resource': '/user/delete', 'user_id_': user_id}
                        resp = controller(request=request)
                        #############################################################
                        messages = resp.get('messages', {})
                        if 'error' in messages:
                            error_messages += messages['error']
                        else:
                            username_list.append(user_username)
                        #############################################################

                if username_list:
                    success_messages.append(f'Were removed the following users: {", ".join(username_list)}')

                st.session_state[editor_key]['deleted_rows'] = []

            # Processar edições
            if st.session_state[editor_key].get('edited_rows'):
                username_list = []
                for index, value in st.session_state[editor_key]['edited_rows'].items():
                    user_id = df.iloc[index]['id']
                    user_name = value.get('name') or df.iloc[index]['name']
                    user_username = value.get('username') or df.iloc[index]['username']
                    user_email = value.get('email') or df.iloc[index]['email']
                    user_status = value.get('status') or df.iloc[index]['status']

                    if 'admin' != user_username:
                        #############################################################
                        ### UPDATE USER BY ID ###
                        #############################################################
                        controller = Controller()
                        request = {
                            'resource': '/user/update_detail',
                            'user_id_': user_id,
                            'user_name': user_name,
                            'user_username': user_username,
                            'user_email': user_email,
                            'user_status': user_status,
                        }
                        resp = controller(request=request)
                        #############################################################
                        messages = resp.get('messages', {})
                        if 'error' in messages:
                            error_messages += messages['error']
                        else:
                            username_list.append(user_username)
                        #############################################################

                if username_list:
                    success_messages.append(f'The following users have been updated: {", ".join(username_list)}')

                st.session_state[editor_key]['edited_rows'] = {}

            # Processar adições
            if st.session_state[editor_key].get('added_rows'):
                error_messages.append('It is not allowed to add new users through the table! Please use the registration form.')
                st.session_state[editor_key]['added_rows'] = []

            # Mostrar mensagens
            if error_messages:
                placeholder_error.error('\n  -'.join(error_messages), icon='🚨')
            if warning_messages:
                placeholder_warning.warning('\n  -'.join(warning_messages), icon='⚠️')
            if success_messages:
                placeholder_success.success('\n  -'.join(success_messages))

            # Rerun para atualizar a tabela
            st.rerun()

        # Processar cancelamento
        if submitted_cancel:
            # Limpar todos os estados de edição
            if st.session_state[editor_key].get('edited_rows'):
                st.session_state[editor_key]['edited_rows'] = {}
            if st.session_state[editor_key].get('deleted_rows'):
                st.session_state[editor_key]['deleted_rows'] = []
            if st.session_state[editor_key].get('added_rows'):
                st.session_state[editor_key]['added_rows'] = []

            st.rerun()


        st.divider()
        st.markdown('### Removed Users')
        #############################################################
        ### GET ALL USERS ###
        #############################################################
        controller = Controller()
        request    = {'resource': '/user/get_removed'}
        resp       = controller(request=request)
        #############################################################
        messages = resp['messages']
        entities = resp['entities']
        #############################################################
        if 'error' in messages:
            st.error('\n  - '.join(messages['error']), icon='🚨')
        if 'info' in messages:
            st.info('\n  - '.join(messages['info']), icon='ℹ️')
        if 'warning' in messages:
            st.warning('\n  - '.join(messages['warning']), icon='⚠️')
        if 'success' in messages:
            st.success('\n  - '.join(messages['success']), icon='✅')
        #############################################################

        if entities:
            df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)

            editor_config = {
                'name': st.column_config.TextColumn('Name (required)', required=True),
                'password': st.column_config.TextColumn('Password'),
                'username': st.column_config.TextColumn('Username'),
                'status': st.column_config.SelectboxColumn('Status', options=['active', 'removed'], required=True),
                'email': st.column_config.TextColumn('E-mail (required)'),
            }

            if 'flag_reset' not in st.session_state:
                st.session_state.flag_reset = False

            placeholder_alert_empty = st.empty()
            placeholder_error_empty = st.empty()
            placeholder_success_empty = st.empty()

            disable_fields = ['password', 'username', 'id', 'name', 'email', 'created_at', 'updated_at']

            if st.session_state.flag_reset:
                editor_update_key = 'update2_data1'
                form_update_key = 'removed_users_form1'
            else:
                editor_update_key = 'update2_data'
                form_update_key = 'removed_users_form'

            # Usar st.form para usuários removidos também
            with st.form(form_update_key):
                edited_df = st.data_editor(df,
                                           num_rows="dynamic",
                                           use_container_width=True,
                                           column_config=editor_config,
                                           disabled=disable_fields,
                                           key=editor_update_key)

                submitted_activate = st.form_submit_button("Ativar Usuários Selecionados", use_container_width=True, type='primary')

            # Processar ativação de usuários
            if submitted_activate:
                username_list = []
                error_messages = []

                if st.session_state[editor_update_key].get('edited_rows'):
                    for index in st.session_state[editor_update_key]['edited_rows']:

                        user_username = df.iloc[index]['username']
                        user_id = df.iloc[index]['id']

                        #############################################################
                        ### ACTIVATE USER BY USERNAME ###
                        #############################################################
                        controller = Controller()
                        request = {'resource': '/user/activate',
                                   'user_username': user_username,
                                   'user_id_': user_id}
                        resp = controller(request=request)
                        #############################################################
                        messages = resp.get('messages', {})
                        if 'error' in messages:
                            error_messages += messages['error']
                        else:
                            username_list.append(user_username)
                        #############################################################

                    if error_messages:
                        placeholder_error_empty.error('\n\n'.join(error_messages), icon='🚨')

                    if username_list:
                        placeholder_success_empty.success(f'Were activated the following users: {", ".join(username_list)}')

                    st.session_state[editor_update_key]['edited_rows'] = {}
                    st.session_state.flag_reset = not st.session_state.flag_reset

                    st.rerun()

    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')
