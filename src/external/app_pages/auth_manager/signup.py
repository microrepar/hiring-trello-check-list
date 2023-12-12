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

            if messages:
                raise Exception('\n\n'.join(messages))
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
    # st.write(entities)

    if messages:
        st.error('\n  -'.join(messages), icon='🚨')
    elif entities:
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        placeholder_data_editor = st.empty()

        editor_config = {
            'name'     : st.column_config.TextColumn('Name (required)', required=True),
            'password' : st.column_config.TextColumn('Password', required=True),
            'username' : st.column_config.TextColumn('Username',  required=True),
            'email'    : st.column_config.TextColumn('E-mail (required)', required=True),
            'status'   : st.column_config.SelectboxColumn('Status', options=['active', 'removed', 'blocked'], required=True),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False
        
        if 'flag_btn_update' not in st.session_state:
            st.session_state.flag_btn_update = False
        
        if 'flag_btn_delete' not in st.session_state:
            st.session_state.flag_btn_delete = False
        
        def on_click_reset_data_editor(*args, **kwargs):
            st.session_state.flag_reset = not st.session_state.flag_reset
            if kwargs.get('key') == 'edited_rows':
                st.session_state[editor_key][kwargs['key']] = {}
            elif kwargs.get('key') == 'deleted_rows':
                st.session_state[editor_key][kwargs['key']] = []
        
        def on_click_btn_update(*args, **kwargs):
            st.session_state.flag_btn_update = kwargs.get('flag', True)
        
        def on_click_btn_delete(*args, **kwargs):
            st.session_state.flag_btn_delete = True

        placeholder_text_area = st.empty()
        cols = st.columns(3)
        with cols[0]:
            placeholder_btn_reset_update = st.empty()
        with cols[1]:
            placeholder_btn_cancelar = st.empty()

        placeholder_alert_empty = st.empty()
        placeholder_error_empty = st.empty()
        placeholder_success_empty = st.empty()
        
        disable_fields = ['id', 'created_at', 'updated_at', 'username']
        visible_fields = []
            
        if st.session_state.flag_reset:
            editor_key = 'update_data1'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        on_change=on_click_btn_update,
                                                        kwargs={'flag': False},
                                                        use_container_width=True,
                                                        key=editor_key)                
        else:
            editor_key = 'update_data'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        on_change=on_click_btn_update,
                                                        kwargs={'flag': False},
                                                        use_container_width=True,
                                                        key=editor_key)
        
        if st.session_state[editor_key].get('deleted_rows'):
            
            flag_contem_admin = False
            
            if not st.session_state.flag_btn_delete:
                
                username_list = list()
                for index in st.session_state[editor_key]['deleted_rows']:                    
                    user_username = df.iloc[index]['username']
                    username_list.append(user_username)
            
                placeholder_text_area.text_area('**:red[CONFIRM EXCLUSION OF THE FOLLOWING USER(S):]**', 
                                                value='- ' + '\n- '.join(username_list),
                                                disabled=True)
            
                placeholder_btn_reset_update.button(f'Confirm Deletion', 
                                                    type='primary',
                                                    on_click=on_click_btn_delete,
                                                    use_container_width=True,
                                                    key='btn_delete')
                
                placeholder_btn_cancelar.button('Cancel',
                                                type='primary',
                                                on_click=on_click_reset_data_editor,
                                                kwargs={'key':'deleted_rows'},
                                                use_container_width=True,
                                                key='reset_update_concluir')
                                                        
            if st.session_state.flag_btn_delete:
                st.session_state.flag_btn_delete = False
                
                error_messages = []
                alert_messages = []            
                username_list = list()
                for index in st.session_state[editor_key]['deleted_rows']:
                    
                    user_username = df.iloc[index]['username']                
                    if user_username and 'admin' in user_username:
                        flag_contem_admin = True                                
                    
                    else:
                        user_id = df.iloc[index]['id'] 
                    #############################################################
                    ### DELETE USER BY ID ###
                    #############################################################
                    controller = Controller()
                    request    = {'resource': '/user/delete',
                                'user_id_': user_id}
                    resp       = controller(request=request)
                    #############################################################
                    messages = resp['messages']
                    entities = resp['entities']

                    if messages:
                        error_messages += messages
                    else:
                        username_list.append(user_username)
                    #############################################################
                
                if flag_contem_admin:
                    alert_messages.append('User "admin" cannot be removed, remove any user except the admin user.')
            
                if error_messages:
                    st.session_state.flag_btn_delete = False
                    placeholder_error_empty.error('\n  -'.join(error_messages), icon='🚨')
                
                if alert_messages:
                    placeholder_alert_empty.warning('\n  -'.join(alert_messages), icon='⚠️')

                if username_list:
                    placeholder_success_empty.success(f'Were removed the following users: {", ".join(username_list)}')


                st.session_state[editor_key]['deleted_rows'] = []
                
        
        if st.session_state[editor_key].get('edited_rows'):
            # st.write(st.session_state[editor_key])

            if not st.session_state.flag_btn_update: 
                placeholder_btn_reset_update.button('Save editions', 
                                                    type='primary',
                                                    on_click=on_click_btn_update,
                                                    use_container_width=True,
                                                    key='btn_update')

                placeholder_btn_cancelar.button('Cancel',
                                                type='primary',
                                                on_click=on_click_reset_data_editor,
                                                kwargs={'key':'edited_rows'},
                                                use_container_width=True,
                                                key='reset_update_concluir')
                                                            
            if st.session_state.flag_btn_update:
                st.session_state.flag_btn_update = False
                
                username_list = []
                error_messages = []
                
                edited_rows = st.session_state[editor_key].get('edited_rows')
                
                for index, value in st.session_state[editor_key]['edited_rows'].items():                    
                    user_id       = df.iloc[index]['id']
                    user_name     = value.get('name') or df.iloc[index]['name']
                    user_username = value.get('username') or df.iloc[index]['username']
                    user_email    = value.get('email') or df.iloc[index]['email']
                    user_status   = value.get('status') or df.iloc[index]['status']

                    if 'admin' == user_username:
                        pass
                    else:
                        #############################################################
                        ### UPDATE USER BY ID ###
                        #############################################################
                        controller = Controller()
                        request    = {
                            'resource'      : '/user/update_detail',
                            'user_id_'      : user_id,
                            'user_name'     : user_name,
                            'user_username' : user_username,
                            'user_email'    : user_email,
                            'user_status'   : user_status,
                        }
                        resp = controller(request=request)
                        #############################################################
                        messages = resp['messages']
                        entities = resp['entities']

                        if messages:
                            error_messages += messages
                        else:
                            username_list.append(user_username)

                        #############################################################
                        

                btn_update_ok = False
                if error_messages:
                    placeholder_error_empty.error('\n  -'.join(error_messages), icon='🚨')                    
                    st.session_state.flag_btn_update = True
                    btn_update_ok = True                        
                
                elif username_list:
                    st.session_state.flag_btn_update = False
                    placeholder_data_editor.success(f'**The following users have been updated:** {", ".join(username_list)}')
                    on_click_reset_data_editor({'key':'edited_rows'})                    
                    placeholder_btn_cancelar.empty()
                    placeholder_btn_reset_update.button('Concluir', use_container_width=True)
                    
                
                if btn_update_ok: 
                    placeholder_btn_cancelar.button('Cancel',
                                                    type='primary',
                                                    on_click=on_click_reset_data_editor,
                                                    kwargs={'key':'edited_rows'},
                                                    use_container_width=True,
                                                    key='reset_update_concluir')
                                                                
                    placeholder_btn_reset_update.button('Save editions', 
                                                        type='primary',
                                                        on_click=on_click_btn_update,
                                                        use_container_width=True,
                                                        key='btn_update')

        if st.session_state[editor_key].get('added_rows'):
            placeholder_alert_empty.error('It is not allowed to add new events through the board! '
                                          'Please click cancel and use the registration form.', icon='🚨')
            placeholder_btn_reset_update.button('Cancel',
                                                    type='primary',
                                                    on_click=on_click_reset_data_editor,
                                                    kwargs={'key':'added_rows'},
                                                    use_container_width=True,
                                                    key='reset_update_concluir')
        

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

        if messages:
            st.error('\n\n'.join(messages), icon='🚨')

        elif entities:
            df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
            placeholder_data_editor = st.empty()

            editor_config = {
                'name': st.column_config.TextColumn('Name (required)', required=True),
                'password': st.column_config.TextColumn('Password'),
                'username': st.column_config.TextColumn('Username'),
                'status': st.column_config.SelectboxColumn('Status', options=['active', 'removed'], required=True),
                'email': st.column_config.TextColumn('E-mail (required)'),
            }

            if 'flag_reset' not in st.session_state:
                st.session_state.flag_reset = False


            # if st.button('Reset', type='primary', key='reset_update'):
            #     st.session_state.flag_reset = not st.session_state.flag_reset
            
            placeholder_alert_empty = st.empty()
            placeholder_error_empty = st.empty()
            placeholder_success_empty = st.empty()
            
            disable_fields = ['password', 'username', 'id', 'name', 'email', 'created_at', 'updated_at']
            if st.session_state.flag_reset:
                editor_update_key = 'update2_data1'
                edited_df = placeholder_data_editor.data_editor(df, 
                                                            num_rows="dynamic", 
                                                            use_container_width=True,
                                                            column_config=editor_config,
                                                            disabled=disable_fields,
                                                            key=editor_update_key)                
            else:
                editor_update_key = 'update2_data'
                edited_df = placeholder_data_editor.data_editor(df, 
                                                            num_rows="dynamic", 
                                                            use_container_width=True,
                                                            column_config=editor_config,
                                                            disabled=disable_fields,
                                                            key=editor_update_key)
            
            if st.session_state[editor_update_key].get('deleted_rows'):  
                placeholder_alert_empty.error('Removing records is not allowed, please use the table up.', icon='🚨')
            
            if st.session_state[editor_update_key].get('edited_rows'): 
                
                for index in st.session_state[editor_update_key]['edited_rows']:
                    
                    user_username = df.iloc[index]['username']
                    user_id = df.iloc[index]['id']
                    user_status = df.iloc[index]['id']

                    username_list = []
                    error_messages = []
                    alert_messages = []
                    #############################################################
                    ### ACTIVATE USER BY USERNAME ###
                    #############################################################
                    controller = Controller()
                    request    = {'resource': '/user/activate',
                                'user_username': user_username,
                                'user_id_': user_id}
                    resp       = controller(request=request)
                    #############################################################
                    messages = resp['messages']
                    entities = resp['entities']

                    if messages:
                        error_messages += messages
                    else:
                        username_list.append(user_username)
                    #############################################################


                if error_messages:
                    placeholder_error_empty.error('\n\n'.join(error_messages), icon='🚨')
                
                if alert_messages:
                    placeholder_alert_empty.warning('\n\n'.join(alert_messages), icon='⚠️')

                if username_list:
                    placeholder_success_empty.success(f'Were activated the following users: {", ".join(username_list)}')

                st.session_state[editor_update_key]['edited_rows'] = {}            
                st.session_state.flag_reset = not st.session_state.flag_reset

                st.rerun()
                

            if st.session_state[editor_update_key].get('deleted_rows'):
                placeholder_alert_empty.error('Removing records by board is not allowed.', icon='🚨')
                

            if st.session_state[editor_update_key].get('added_rows'):
                placeholder_alert_empty.error('Adding new records by board is not allowed, please use the form to add new users.', icon='🚨')
    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')    
