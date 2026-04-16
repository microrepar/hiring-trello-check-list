import contextlib
from pathlib import Path
import hashlib
import streamlit as st
import pandas as pd
import subprocess

from streamlit_js_eval import (copy_to_clipboard, create_share_link,
                                       get_geolocation, streamlit_js_eval)

from src.adapters import Controller

candidate_columns = ['nome', 'insc', 'classif', 'cargo', 'convocacao', 'prazo', 'edital', 'secretaria' ]
candidate_types   = [ str,    str,    str,      str,  'datetime64[ns]', 'datetime64[ns]', str, str]


def get_dataframe_hash(df):
    """Calcula o hash do DataFrame para detectar alterações"""
    # Converter DataFrame para string CSV de forma consistente
    df_string = df.to_csv(index=False).encode('utf-8')
    return hashlib.md5(df_string).hexdigest()


def on_click_flag_reset():
    st.session_state.flag_reset = not st.session_state.flag_reset

def on_quantity_change():
    """Callback quando a quantidade muda - mantém o reset do form"""
    on_click_flag_reset()


def candidate_list_page(username, user_dict, placeholder_messages):

    #############################################################
    ### REGISTRY TRELLO CHECKLIST###
    #############################################################
    request = {
        'resource'   : '/convocation/get_edital_label_list',
    }
    #############################################################
    controller = Controller()
    resp = controller(request=request)
    messages = resp.get('messages')

    edital_dict = {}
    if resp.get('objects'):
        edital_dict = resp.get('objects')[-1]
    
    label_list = [' '] + list(edital_dict)
    #############################################################
    if 'error' in messages:
        placeholder_messages.error('Verifique os erros apresentados abaixo', icon='🚨')
        st.error('\n  - '.join(messages['error']), icon='🚨')        
    if 'info' in messages:
        placeholder_messages.info('\n  - '.join(messages['info']), icon='⚠️')
        st.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placeholder_messages.info('\n  - '.join(messages['warning']), icon='ℹ️')
        st.warning('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placeholder_messages.info('\n  - '.join(messages['success']), icon='✅')
        st.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################
    

    if 'flag_reset' not in st.session_state:
        st.session_state.flag_reset = False

    # Controle de alterações via comparação de hash
    if 'current_df_hash' not in st.session_state:
        st.session_state.current_df_hash = None

    if 'saved_df_hash' not in st.session_state:
        st.session_state.saved_df_hash = None

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
        # Inicializar o hash salvo para o DataFrame vazio
        st.session_state.saved_df_hash = get_dataframe_hash(df)

    col1, *cols = st.columns(5)
    qtd_convocados = col1.number_input('Quantidade:',
                                       value=1,
                                       format='%d',
                                       on_change=on_quantity_change,
                                       min_value=1)

    df = pd.read_pickle(candidates_file)

    # Inicializar o hash salvo na primeira carga ou após reset
    if st.session_state.saved_df_hash is None:
        st.session_state.saved_df_hash = get_dataframe_hash(df)

    qtd_inseridos = df.shape[0]

    # Ajustar o DataFrame para ter exatamente a quantidade desejada
    if qtd_inseridos > qtd_convocados:
        # Se há mais registros do que a quantidade desejada, cortar o DataFrame
        df = df.iloc[:qtd_convocados].copy()
        df.to_pickle(candidates_file)
        # Atualizar hash salvo pois o sistema alterou os dados
        st.session_state.saved_df_hash = get_dataframe_hash(df)
        if qtd_inseridos > 0:  # Só mostrar mensagem se havia registros antes
            st.info(f"📝 Quantidade reduzida de {qtd_inseridos} para {qtd_convocados} registros. Os registros excedentes foram removidos.")
    elif qtd_inseridos < qtd_convocados:
        # Se há menos registros, adicionar linhas vazias
        qtd_adicionar = qtd_convocados - qtd_inseridos
        empty_df = pd.DataFrame([{} for _ in range(qtd_adicionar)])
        df = pd.concat([df, empty_df], ignore_index=True)
        df.fillna('', inplace=True)
        df = df.astype(dict(zip(candidate_columns, candidate_types)))
        df.to_pickle(candidates_file)
        # Atualizar hash salvo pois o sistema alterou os dados
        st.session_state.saved_df_hash = get_dataframe_hash(df)
        st.info(f"➕ Adicionados {qtd_adicionar} registros em branco para completar a quantidade de {qtd_convocados}.")

    editor_config = {
        'nome': st.column_config.TextColumn('Nome Completo', required=True, default=''),
        'insc': st.column_config.TextColumn('Inscrição', required=True, default=''),
        'classif': st.column_config.TextColumn('Classificação', required=True, default=''),
        'cargo': st.column_config.TextColumn('Cargo', required=True, default=''),
        'convocacao': st.column_config.DateColumn('Data Convocação', required=True, format='DD/MM/YYYY'),
        'prazo': st.column_config.DateColumn('Prazo Final', required=True, format='DD/MM/YYYY'),
        'edital': st.column_config.SelectboxColumn('Edital', options=label_list, required=True),
        'secretaria': st.column_config.TextColumn('Secretaria', required=True, default=''),
    }

    placeholder_data_editor = st.empty()

    if st.session_state.flag_reset:
        editor_key = 'update_data1'
        form_key = 'candidate_form1'
    else:
        editor_key = 'update_data'
        form_key = 'candidate_form'

    # Colocar o data_editor de VOLTA dentro do form para evitar reruns
    with placeholder_data_editor.form(form_key):
        placeholder_warning_form = st.empty()

        edited_df = st.data_editor(df,
                                   num_rows="dynamic",
                                   column_config=editor_config,
                                   use_container_width=True,
                                   key=editor_key)

        # Botão de submit que salva e cria o checklist
        col_btn_save, col_btn_reset = st.columns(2)
        with col_btn_save:
            submitted = st.form_submit_button("🗂️ Criar Checklist", use_container_width=True, type='primary')
        with col_btn_reset:
            reset_form = st.form_submit_button("🔄 Resetar Dados", use_container_width=True, on_click=on_quantity_change)

    # Salva automaticamente as alterações e cria o checklist
    # Processar apenas quando o formulário for submetido
    if submitted:
        
        # Salvar as alterações no arquivo
        edited_df.to_pickle(candidates_file)

        # Atualizar o hash salvo para refletir as alterações salvas
        st.session_state.saved_df_hash = get_dataframe_hash(edited_df)

        # Limpar os estados de edição
        if st.session_state[editor_key].get('added_rows'):
            st.session_state[editor_key]['added_rows'] = []
        if st.session_state[editor_key].get('edited_rows'):
            st.session_state[editor_key]['edited_rows'] = {}
        if st.session_state[editor_key].get('deleted_rows'):
            st.session_state[editor_key]['deleted_rows'] = []

        # Criar o checklist automaticamente
        if not edited_df.empty:
            # Recarregar do arquivo para garantir dados atualizados
            df_saved = pd.read_pickle(candidates_file)

            df_copy = df_saved.copy()
            df_copy['edital'] = df_copy['edital'].replace(edital_dict)
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
                placeholder_messages.error('Verifique os erros apresentados abaixo', icon='🚨')
                st.error('\n  - '.join(messages['error']), icon='🚨')
            if 'info' in messages:
                placeholder_messages.info('\n  - '.join(messages['info']), icon='⚠️')
                st.info('\n  - '.join(messages['info']), icon='⚠️')
            if 'warning' in messages:
                placeholder_messages.info('\n  - '.join(messages['warning']), icon='ℹ️')
                st.warning('\n  - '.join(messages['warning']), icon='ℹ️')
            if 'success' in messages:
                st.session_state.messages_success = messages

                if entities:
                    convocation = entities[-1]
                    df = pd.concat([pd.DataFrame(c.data_to_dataframe()) for c in convocation.candidates])
                else:
                    # Apaga o registros após serem inseridos
                    df = pd.DataFrame(columns=candidate_columns)
                    df = df.astype(dict(zip(candidate_columns, candidate_types)))

                # Limpar o DataFrame após criar checklist e resetar
                df.to_pickle(candidates_file)

                on_click_flag_reset()
                st.rerun()
            #############################################################
    
    if reset_form:                    
        df = pd.DataFrame(columns=candidate_columns)
        df = df.astype(dict(zip(candidate_columns, candidate_types)))
        df.to_pickle(candidates_file)
        st.rerun()

    if st.session_state.get('messages_success'):
        messages = st.session_state['messages_success']
        placeholder_messages.success('\n  - '.join(messages['success']), icon='✅')
        st.success('\n  - '.join(messages['success']), icon='✅')
        del st.session_state['messages_success']

    # st.write(st.session_state[editor_key])
    # st.write(list(edited_df.T.to_dict().values()))
