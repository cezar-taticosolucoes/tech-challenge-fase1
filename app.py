import streamlit as st
import streamlit_option_menu
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts
import pandas as pd
from utils.data_exportacao import process_file
from utils.data_importacao import process_file_import
from utils.data_comercio import process_file_comercio
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Configuração inicial
st.set_page_config(
    page_title='Analytics | Vinhos',
    page_icon='🍷',
    layout='centered'
)

with st.sidebar:
    option = option_menu(
        menu_title="Navegação",
        options=["Home", "Analytics", "Exportações", "Importações", "Comercialização"],
        icons=["house", "bar-chart", "arrow-up-square", "arrow-down-square", "box"],
        menu_icon="card-list",
        default_index=0
    )

# Configurar a conexão com o banco de dados PostgreSQL
db_url = "postgresql://db_app_personal:PB6cGDCHizDVGfW71Bqaeme56B4EAqOV@dpg-ctdo04rgbbvc73fk9tv0-a.oregon-postgres.render.com/db_app_personal_ip2i"
engine = create_engine(db_url)

if option == 'Analytics':
    st.title('Data Analytics')
    
    #### Sessão Analytics Exportação ####
    # Consulta SQL
    query = '''
    SELECT "País",
           SUM("Quantidade") AS Quantidade, 
           SUM("Valor") AS Valor
    FROM exportacoes_vinho 
    GROUP BY "País" 
    ORDER BY "País";
    '''
    df = pd.read_sql(query, engine)

    st.subheader('Exportação de Vinho | País de Origem: Brasil')

    # Entrada do usuário para filtro
    with st.expander('Pesquise por um País'):
        search = st.text_input('', '')

    # **Filtro dinâmico**
    if search.strip():
        filtered_df = df[df["País"].str.contains(search.strip(), case=False, na=False)]
    else:
        filtered_df = df.copy()

    # **Cálculo das métricas filtradas**
    total_quantity = filtered_df["quantidade"].sum()
    total_value = filtered_df["valor"].sum()

    # **Formatação de valores para exibição**
    quantidade_formatada = f"{total_quantity:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_formatado = f"{total_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # **Exibição de métricas**
    col1, col2 = st.columns(2)
    col1.metric("🍷 Quantidade Total (L)", quantidade_formatada)
    col2.metric("💵 Valor Total (US$)", valor_formatado)

    # **Exibição da tabela com os dados filtrados**
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            width=800,
            hide_index=True,
            column_config={
                'quantidade': st.column_config.NumberColumn('Quantidade (L)', format='%.2f'),
                'valor': st.column_config.NumberColumn('Valor (US$)', format='%.2f')
            }
        )
    else:
        st.warning("Nenhum resultado encontrado para o termo pesquisado.")

elif option == 'Exportações':
    st.title('Tratamento de Dados - Exportações')
    st.header('Exportação de Vinhos')

    # Upload de arquivos
    uploaded_files = st.file_uploader(
        'Faça upload dos arquivos csv:',
        accept_multiple_files=True,
        type=['csv'],
        help='O upload dos arquivos deve ser feito exatamente como foram feitos os downloads do site.'
    )

    if uploaded_files:
        consolidated_data = pd.DataFrame()

        for uploaded_file in uploaded_files:
            # Carregar o arquivo em um DataFrame
            df = pd.read_csv(uploaded_file, sep=';')

            # Processar o DataFrame usando o arquivo `data_exportacao.py`
            processed_data = process_file(uploaded_file.name, df)

            # Concatenar o DataFrame processado ao consolidado
            consolidated_data = pd.concat(
                [consolidated_data, processed_data], ignore_index=True)

        # Exibir os dados processados na interface
        st.write('Dados processados:')
        st.dataframe(
            consolidated_data,
            width=800,
            hide_index=True,
            column_config={
                'Quantidade': st.column_config.NumberColumn('Quantidade (Kg)', format="%.2f"),
                'Valor': st.column_config.NumberColumn('Valor (US$)', format="%.2f")
            }
        )

        # Botão para salvar os dados no banco de dados
        if st.button('Salvar dados no banco de dados'):
            try:
                table_name = 'exportacoes_vinho'
                with engine.connect() as connection:
                    try:
                        existing_data = pd.read_sql(
                            f"SELECT * FROM {table_name}", connection)
                    except SQLAlchemyError:
                        existing_data = pd.DataFrame()  # Caso a tabela não exista

                # Remover duplicados comparando com os dados existentes
                if not existing_data.empty:
                    consolidated_data = consolidated_data[~consolidated_data.isin(
                        existing_data.to_dict(orient='list')).all(axis=1)]

                # Salvar novos dados no banco de dados
                if not consolidated_data.empty:
                    consolidated_data.to_sql(
                        table_name, engine, if_exists='append', index=False)
                    st.success(f'Dados salvos com sucesso na tabela `{table_name}` do banco de dados!')
                else:
                    st.warning('Os dados já existem no banco de dados.')
            except Exception as e:
                st.error(f'Erro ao salvar os dados no banco de dados: {e}')

elif option == 'Importações':
    st.title('Tratamento de Dados - Importações')
    st.header('Importação de Vinhos')

    # Upload de arquivos
    uploaded_files = st.file_uploader(
        'Faça upload dos arquivos csv:',
        accept_multiple_files=True,
        type=['csv'],
        help='O upload dos arquivos deve ser feito exatamente como foram feitos os downloads do site.'
    )

    if uploaded_files:
        consolidated_data = pd.DataFrame()

        for uploaded_file in uploaded_files:
            # Carregar o arquivo em um DataFrame
            df = pd.read_csv(uploaded_file, sep=';')

            # Processar o DataFrame usando o arquivo `data_importacao.py`
            processed_data = process_file_import(uploaded_file.name, df)

            # Concatenar o DataFrame processado ao consolidado
            consolidated_data = pd.concat(
                [consolidated_data, processed_data], ignore_index=True)

        # Exibir os dados processados na interface
        st.write('Dados processados:')
        st.dataframe(
            consolidated_data,
            width=800,
            hide_index=True,
            column_config={
                'Quantidade': st.column_config.NumberColumn('Quantidade (Kg)', format="%.2f"),
                'Valor': st.column_config.NumberColumn('Valor (US$)', format="%.2f")
            }
        )

        # Botão para salvar os dados no banco de dados
        if st.button('Salvar dados no banco de dados'):
            try:
                table_name = 'importacoes_vinho'
                with engine.connect() as connection:
                    try:
                        existing_data = pd.read_sql(
                            f"SELECT * FROM {table_name}", connection)
                    except SQLAlchemyError:
                        existing_data = pd.DataFrame()  # Caso a tabela não exista

                # Remover duplicados comparando com os dados existentes
                if not existing_data.empty:
                    consolidated_data = consolidated_data[~consolidated_data.isin(
                        existing_data.to_dict(orient='list')).all(axis=1)]

                # Salvar novos dados no banco de dados
                if not consolidated_data.empty:
                    consolidated_data.to_sql(
                        table_name, engine, if_exists='append', index=False)
                    st.success(f'Dados salvos com sucesso na tabela `{table_name}` do banco de dados!')
                else:
                    st.warning('Os dados já existem no banco de dados.')
            except Exception as e:
                st.error(f'Erro ao salvar os dados no banco de dados: {e}')

elif option == 'Comercialização':
    st.title('Tratamento de Dados - Comercialização')
    st.header('Comercialização de Produtos')

    # Upload de arquivos
    uploaded_files = st.file_uploader(
        'Faça upload dos arquivos csv:',
        accept_multiple_files=True,
        type=['csv'],
        help='O upload dos arquivos deve ser feito conforme o formato esperado.'
    )

    if uploaded_files:
        consolidated_data = pd.DataFrame()

        for uploaded_file in uploaded_files:
            # Carregar o arquivo em um DataFrame
            df = pd.read_csv(uploaded_file, sep=';')

            # Processar o DataFrame usando o arquivo `data_comercio.py`
            processed_data = process_file_comercio(df)

            # Concatenar o DataFrame processado ao consolidado
            consolidated_data = pd.concat(
                [consolidated_data, processed_data], ignore_index=True)

        # Exibir os dados processados na interface
        st.write('Dados processados:')
        st.dataframe(
            consolidated_data,
            width=800,
            hide_index=True,
            column_config={
                'Quantidade': st.column_config.NumberColumn('Quantidade', format='%.2f')
            }
        )

        # Botão para salvar os dados no banco de dados
        if st.button('Salvar dados no banco de dados'):
            try:
                table_name = 'comercializacao_produtos'
                with engine.connect() as connection:
                    try:
                        existing_data = pd.read_sql(
                            f"SELECT * FROM {table_name}", connection)
                    except SQLAlchemyError:
                        existing_data = pd.DataFrame()  # Caso a tabela não exista

                # Remover duplicados comparando com os dados existentes
                if not existing_data.empty:
                    consolidated_data = consolidated_data[~consolidated_data.isin(
                        existing_data.to_dict(orient='list')).all(axis=1)]

                # Salvar novos dados no banco de dados
                if not consolidated_data.empty:
                    consolidated_data.to_sql(
                        table_name, engine, if_exists='append', index=False)
                    st.success(f'Dados salvos com sucesso na tabela `{table_name}` do banco de dados!')
                else:
                    st.warning('Os dados já existem no banco de dados.')
            except Exception as e:
                st.error(f'Erro ao salvar os dados no banco de dados: {e}')

# Obter o ano atual
current_year = datetime.now().year

# Adicionar rodapé com informações de direitos autorais
st.markdown(f"""
    <style>
    footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }}
    </style>
    <footer>
        {current_year} - Cézar Maldini. Todos os direitos reservados.
    </footer>
""", unsafe_allow_html=True)