import contextlib
from pathlib import Path
import streamlit as st
import pandas as pd
import subprocess

from streamlit_js_eval import (copy_to_clipboard, create_share_link,
                                       get_geolocation, streamlit_js_eval)

from src.adapters import Controller

candidate_columns = ['nome', 'insc', 'classif', 'cargo', 'convocacao', 'prazo', 'edital', 'secretaria' ]
candidate_types   = [ str,    str,    str,      str,  'datetime64[ns]', 'datetime64[ns]', str, str]


def candidate_list_page(username, user_dict, placeholder_messages):

    with contextlib.suppress(FileExistsError):
        Path(f'pickle_data').mkdir()
    
    with contextlib.suppress(FileExistsError):
        Path(f'pickle_data/{username}').mkdir()

    candidates_file = Path(f'pickle_data/{username}/candidates.pkl')

    st.markdown('### LISTA DE CANDIDATOS')
    if not candidates_file.exists():
        df = pd.DataFrame(columns=candidate_columns)
        df = df.astype(dict(zip(candidate_columns, candidate_types)))
        df.to_pickle(candidates_file)

    col1, *cols = st.columns(5)
    qtd_convocados = col1.number_input('Quantidade de convocados:', value=1, format='%d', min_value=1)

    df = pd.read_pickle(candidates_file)


    qtd_inseridos = df.shape[0]
    if qtd_inseridos >= qtd_convocados:
        qtd_convocados = 0
    else:
        qtd_convocados = qtd_convocados - qtd_inseridos

    # Criando um DataFrame com linhas vazias
    empty_df = pd.DataFrame([{} for _ in range(qtd_convocados)])

    # Concatenando o DataFrame vazio ao DataFrame original
    df = pd.concat([df, empty_df], ignore_index=True)

    editor_config = {
        'nome': st.column_config.TextColumn('Nome Completo', required=True, default=''),
        'insc': st.column_config.TextColumn('Inscrição', required=True, default=''),
        'classif': st.column_config.TextColumn('Classificação', required=True, default=''),
        'cargo': st.column_config.TextColumn('Cargo', required=True, default=''),
        'convocacao': st.column_config.DateColumn('Data Convocação', required=True, format='DD/MM/YYYY'),
        'prazo': st.column_config.DateColumn('Prazo Final', required=True, format='DD/MM/YYYY'),
        'edital': st.column_config.TextColumn('Edital', required=True, default=''),
        'secretaria': st.column_config.TextColumn('Secretaria', required=True, default=''),
    }
    
    placeholder_data_editor = st.empty()

    if 'flag_reset' not in st.session_state:
        st.session_state.flag_reset = False


    if st.session_state.flag_reset:
        editor_key = 'update_data1'
        edited_df = placeholder_data_editor.data_editor(df, 
                                                    num_rows="dynamic", 
                                                    column_config=editor_config,
                                                    use_container_width=True,
                                                    key=editor_key)                
    else:
        editor_key = 'update_data'
        edited_df = placeholder_data_editor.data_editor(df, 
                                                    num_rows="dynamic", 
                                                    column_config=editor_config,
                                                    use_container_width=True,
                                                    key=editor_key)
        

    if st.session_state[editor_key].get('added_rows'):
        st.session_state.flag_reset = not st.session_state.flag_reset
        edited_df.to_pickle(candidates_file)
        st.session_state[editor_key]['added_rows'] = []
        st.rerun()

    if st.session_state[editor_key].get('edited_rows'):
        st.session_state.flag_reset = not st.session_state.flag_reset
        edited_df.to_pickle(candidates_file)
        st.session_state[editor_key]['edited_rows'] = {}
        st.rerun()
    
    if st.session_state[editor_key].get('deleted_rows'):
        st.session_state.flag_reset = not st.session_state.flag_reset
        edited_df.to_pickle(candidates_file)
        st.session_state[editor_key]['deleted_rows'] = []
        st.rerun()

    
    # st.write(st.session_state[editor_key])
    # st.write(list(edited_df.T.to_dict().values()))
    
    placeholder_btn_criar_checklist = st.empty()
    
    if not edited_df.empty:
        if placeholder_btn_criar_checklist.button('Criar Checklist'):

            df_copy = edited_df.copy()
            df_copy['convocacao'] = df_copy['convocacao'].astype(str)
            df_copy['prazo'] = df_copy['prazo'].astype(str)

            cols_to_rename = {
                "nome"       : "candidate_complete_name",
                "insc"       : "candidate_enrollment",
                "classif"    : "candidate_classification",
                "cargo"      : "candidate_office",
                "convocacao" : "candidate_convocation_date",
                "prazo"      : "candidate_deadline",
                "edital"     : "candidate_notice",
                "secretaria" : "candidate_department",
            }

            df_copy.rename(columns=cols_to_rename, inplace=True)
            df_copy.fillna('', inplace=True)
            # st.write(list(df_copy.T.to_dict().values()))
           
            #############################################################
            ### REGISTRY TRELLO CHECKLIST###
            #############################################################
            request = {
                'resource'   : '/convocation/create_checklist',
                'convocation_created_by' : username,
                'convocation_candidates' : list(df_copy.T.to_dict().values()),
            }
            #############################################################
            controller = Controller()
            resp = controller(request=request)
            messages = resp.get('messages')
            entities = resp.get('entities')
            #############################################################

            if 'error' in messages:
                placeholder_messages.error('\n  - '.join(messages['error']), icon='🚨')
                st.error('\n  - '.join(messages['error']), icon='🚨')
            if 'info' in messages:
                placeholder_messages.info('\n  - '.join(messages['info']), icon='⚠️')
                st.info('\n  - '.join(messages['info']), icon='⚠️')
            if 'warning' in messages:
                placeholder_messages.info('\n  - '.join(messages['warning']), icon='ℹ️')
                st.info('\n  - '.join(messages['warning']), icon='ℹ️')
            if 'success' in messages:
                placeholder_messages.info('\n  - '.join(messages['success']), icon='✅')
                st.info('\n  - '.join(messages['success']), icon='✅')
                
                if entities:
                    convocation = entities[-1]
                    df = pd.concat([pd.DataFrame(c.data_to_dataframe()) for c in convocation.candidates])
                else:                        
                    # Apaga o registros após serem inseridos
                    df = pd.DataFrame(columns=candidate_columns)
                    df = df.astype(dict(zip(candidate_columns, candidate_types)))
                
                df.to_pickle(candidates_file)
                placeholder_btn_criar_checklist.button('Concluir')
            #############################################################






