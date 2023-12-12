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


def candidate_list_page(username, user_dict):
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
        'nome': st.column_config.TextColumn('Nome Completo', required=True),
        'insc': st.column_config.TextColumn('Inscrição', required=True),
        'classif': st.column_config.TextColumn('Classificação', required=True),
        'cargo': st.column_config.TextColumn('Cargo', required=True),
        'convocacao': st.column_config.DateColumn('Data Convocação', required=True, format='DD/MM/YYYY'),
        'prazo': st.column_config.DateColumn('Prazo Final', required=True, format='DD/MM/YYYY'),
        'edital': st.column_config.TextColumn('Edital', required=True),
        'secretaria': st.column_config.TextColumn('Secretaria', required=True),
    }
    
    placeholder_data_editor = st.empty()

    if 'flag_reset' not in st.session_state:
        st.session_state.flag_reset = False


    if st.session_state.flag_reset:
        editor_key = 'update_data1'
        edited_df = placeholder_data_editor.data_editor(df, 
                                                    num_rows="dynamic", 
                                                    column_config=editor_config,
                                                    # hide_index=True,
                                                    use_container_width=True,
                                                    key=editor_key)                
    else:
        editor_key = 'update_data'
        edited_df = placeholder_data_editor.data_editor(df, 
                                                    num_rows="dynamic", 
                                                    column_config=editor_config,
                                                    # hide_index=True,
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

    if not edited_df.empty:
        if st.button('Criar Checklist'):
            df = pd.DataFrame(columns=candidate_columns)
            df = df.astype(dict(zip(candidate_columns, candidate_types)))
            df.to_pickle(candidates_file)
            st.rerun()


