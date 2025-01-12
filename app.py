# Import de bibliotecas do Streamlit
import streamlit as st
import streamlit_option_menu
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts

# Import de Funções da Pasta utils/
from utils.pipeline_export import process_file
from utils.pipeline_import import process_file_import
from utils.pipeline_comercio import process_file_comercio
from utils.functions import format_number, converte_csv, mensagem_sucesso

# Outras bibliotecas
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import time
import pandas as pd
import plotly.express as px

# Configuração inicial da Aplicação Streamlit
st.set_page_config(
    page_title='Analytics | Vinhos',
    page_icon='🍷',
    layout='wide'
)

# Navegação da Aplicação Streamlit
with st.sidebar:
    option = option_menu(
        menu_title="Navegação",
        options=["Home", "Analytics", "Upload"],
        icons=["house", "bar-chart", "arrow-up-square"],
        menu_icon="card-list",
        default_index=0
    )

# Configurar a conexão com o banco de dados PostgreSQL
db_url = "postgresql://db_data_tech:dxNVQ2xbdjHmABoVE84CYMGnyo8EOasa@dpg-cu1qptpu0jms738l9cog-a.oregon-postgres.render.com/db_data_tech"
engine = create_engine(db_url)


#### Tabelas para montagem dos Dashboards ####
# Consulta SQL Tabela: export_vinho
# Buscar o ano mais recente na base de dados
query_max_year = '''
SELECT MAX(CAST("Ano" AS INTEGER)) AS ano_mais_recente
FROM export_vinho;
'''
# Executa a consulta para obter o ano mais recente
result = pd.read_sql(query_max_year, engine)

# Converte o ano mais recente para inteiro
ano_mais_recente = int(result.loc[0, 'ano_mais_recente'])

# Define o limite de anos baseado no ano mais recente
ano_limite = ano_mais_recente - 15

# Consulta SQL para buscar os últimos 15 anos
query_export = f'''
SELECT *
FROM export_vinho
WHERE CAST("Ano" AS INTEGER) >= {ano_limite};
'''
# Executa a consulta com o filtro
df_export = pd.read_sql(query_export, engine).sort_values('Ano', ascending=True)
df_export['Ano'] = df_export['Ano'].astype(int)


### Página Analytics ###
if option == 'Analytics':
    st.title('Data Analytics')

    ### Visualização no Streamlit ###
    tab1, tab2, tab3 = st.tabs(['Exportação', 'Importação', 'Comercialização'])

    ### Analytics Exportação ###
    with tab1:
        st.subheader('Exportação de Vinho | País de Origem: Brasil')
        st.markdown(f'Período: {ano_limite} - {ano_mais_recente}')

        sub_tab1, sub_tab2 = st.tabs(['Dashboard 📊', 'Table 📅'])

        ### Exportação: Dashboard
        with sub_tab1:
            with st.container():
                # Filtros
                with st.expander('Filtros'):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # Filtro Número de Países
                        number_paises = st.number_input('Número de países a serem análisados', min_value=2, max_value=15, value=5, help='Selecionar o número de Países que serão análisados: de 2 a 15.')
                    with col2:
                        # Filtro de Tipo
                        tipos_disponiveis = df_export['Tipo'].dropna().unique()  # Obtém os tipos únicos
                        tipo_selecionado = st.multiselect(
                            "Selecione o(s) Tipo(s):",
                            options=tipos_disponiveis,
                            default=tipos_disponiveis
                        )
                    with col3:
                        # Filtro de Período
                        year = st.slider(
                            "Selecione um Período de Anos",
                            df_export['Ano'].min(),
                            df_export['Ano'].max(),
                            (df_export['Ano'].min(), df_export['Ano'].max()),
                            key="year_slider"
                        )
                
                # Aplicar filtros no DataFrame
                df_filtered = df_export[
                    (df_export['Ano'] >= year[0]) & 
                    (df_export['Ano'] <= year[1]) &
                    (df_export['Tipo'].isin(tipo_selecionado))
                ]

                # Filtrar os países com maior valor dentro do intervalo e tipo selecionados
                top_countries = (
                    df_filtered.groupby('País')['Valor']
                    .sum()
                    .nlargest(number_paises)
                    .index
                )
                df_filtered = df_filtered[df_filtered['País'].isin(top_countries)]

                # Agregar os dados por Ano e País
                df_export_agg = (
                    df_filtered.groupby(['Ano', 'País'], as_index=False)['Valor']
                    .sum()
                )

                #### Criação dos Gráficos ####
                # Gráfico de barras - Valor
                df_valor_pais = (
                    df_filtered.groupby('País', as_index=False)['Valor']
                    .sum()
                    .nlargest(number_paises, 'Valor')
                )

                # Garante a ordem dos países baseada nos valores
                country_order_valor = df_valor_pais.sort_values('Valor', ascending=False)['País'].tolist()

                fig_valor_pais = px.bar(
                    df_valor_pais,
                    x='Valor',
                    y='País',
                    text_auto='.2s',
                    title=f"Valor (US$): Top {number_paises} Países",
                    color_discrete_sequence=['#F1145C'],
                    category_orders={"País": country_order_valor},
                    hover_data={'País': True, 'Valor': ':.2f'},
                    height=500 + (number_paises - 5) * 50
                )

                # Gráfico de barras - Quantidade
                df_quant_pais = (
                    df_filtered.groupby('País', as_index=False)['Quantidade']
                    .sum()
                    .nlargest(number_paises, 'Quantidade')
                )

                # Garante a ordem dos países baseada nas quantidades
                country_order_quant = df_quant_pais.sort_values('Quantidade', ascending=False)['País'].tolist()

                fig_quant_pais = px.bar(
                    df_quant_pais,
                    x='Quantidade',
                    y='País',
                    text_auto='.2s',
                    title=f"Quantidade Total (L): Top {number_paises} Países",
                    color_discrete_sequence=['#F1145C'],
                    category_orders={"País": country_order_quant},
                    hover_data={'País': True, 'Quantidade': ':.2f'},
                    height=500 + (number_paises - 5) * 50
                )

                # Gráfico de linhas - Valor por Ano
                fig_valor_ano_pais = px.line(
                    df_export_agg,
                    x='Ano',
                    y='Valor',
                    color='País',
                    range_y=(df_export_agg['Valor'].min() - 1000000, df_export_agg['Valor'].max() + 1000000),
                    markers=True,
                    title=f"Valor por Ano (US$): Top {number_paises} Países",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    hover_data={'Ano': True, 'Valor': ':.2f'}
                )

                # Gráficos de Barras
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f'💵 Valor Total (US$): Top {number_paises} Países', format_number(df_valor_pais['Valor'].sum()))
                    st.plotly_chart(fig_valor_pais, use_container_width=True)
                with col2:
                    st.metric(f'🍷 Quantidade Total (L): Top {number_paises} Países', format_number(df_quant_pais['Quantidade'].sum()))
                    st.plotly_chart(fig_quant_pais, use_container_width=True)

                st.plotly_chart(fig_valor_ano_pais, use_container_width=True)

        # Exportação: Sessão Tables
        with sub_tab2:
            # Entrada do usuário para filtro
            with st.expander('Filtros'):
                col1, col2, col3 = st.columns(3)
                with col1:
                    pais = st.multiselect('Selecione um país', pd.Series(df_export['País'].unique()).sort_values(ascending=True))
                with col2:
                    tipo = st.multiselect('Selecione os tipos', pd.Series(df_export['Tipo'].unique()).sort_values(ascending=True))
                with col3:
                    year = st.slider('Selecione um Período de Anos', 
                                    df_export['Ano'].min(), 
                                    df_export['Ano'].max(), 
                                    (df_export['Ano'].min(), df_export['Ano'].max()))

            # Aplicando os filtros no DataFrame
            df_filtrado = df_export.copy()

            if pais:
                df_filtrado = df_filtrado[df_filtrado['País'].isin(pais)]
            if tipo:
                df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipo)]
            if year:
                df_filtrado = df_filtrado[
                    (df_filtrado['Ano'] >= year[0]) & (df_filtrado['Ano'] <= year[1])
                ]

            # Cálculo das métricas filtradas
            total_quantity = df_filtrado["Quantidade"].sum()
            total_value = df_filtrado["Valor"].sum()

            # Formatação de valores para exibição
            quantidade_formatada = format_number(total_quantity)
            valor_formatado = format_number(total_value)

            # Exibição de métricas
            col1, col2 = st.columns(2)
            with col1:
                col1.metric("💵 Valor Total (US$)", valor_formatado)
            with col2:
                col2.metric("🍷 Quantidade Total (L)", quantidade_formatada)

            # Exibição da tabela com os dados filtrados
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado,
                    hide_index=True,
                    width=2000,
                    column_config={
                        'Quantidade': st.column_config.NumberColumn('Quantidade (L)', format='%.2f'),
                        'Valor': st.column_config.NumberColumn('Valor (US$)', format='%.2f'),
                        'Ano': st.column_config.NumberColumn('Ano', format='%d')
                    }
                )
            else:
                st.warning("Nenhum resultado encontrado para os filtros aplicados.")
            
            st.markdown(
                f"""
                <p>A tabela possui <span style="color:#F1145C;">{df_filtrado.shape[0]}</span> linhas.
                """, 
                unsafe_allow_html=True
            )

            st.markdown('Escreva um nome para o arquivo')
            coluna1, coluna2 = st.columns(2)
            with coluna1:
                nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
                nome_arquivo += '.csv'
            with coluna2:
                st.download_button('Download', data = converte_csv(df_filtrado), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso, help='Clique para fazer download dos dados em formato csv.')

    ### Analytics Importações ###
    with tab2:
        st.subheader('Importação de Vinho | País de Destino: Brasil')

        st.markdown(f'Período: {ano_limite} - {ano_mais_recente}')

        sub_tab1, sub_tab2 = st.tabs(['Dashboard 📊', 'Table 📅'])

elif option == 'Upload':
    st.title('Upload de Dados')

    with st.expander('Processamento dos Dados'):
        st.markdown("""
        1. **Download dos arquivos CSV no site:**
        - Acesse o site [VITIBRASIL - Embrapa](http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_01) e faça o download dos arquivos CSV desejados.

        2. **Upload dos arquivos no app:**
        - Utilize o botão abaixo para fazer o upload dos arquivos CSV no seu aplicativo.

        3. **Tratamento e armazenamento no Banco de Dados PostgreSQL:**
        - O aplicativo irá processar os arquivos CSV e armazená-los no Banco de Dados PostgreSQL para a utilização no módulo de Analytics.
        """)

        st.image('https://i.ibb.co/WfLxmdh/Data-Pipeline-Tech-Challenge.jpg')

    tab1, tab2, tab3 = st.tabs(
        ['Exportações', 'Importações', 'Comercialização'])

    ### Upload de Dados de Exportação ###
    with tab1:
        st.header('Exportação de Vinhos')

        with st.expander('Modelos de Arquivos'):
            st.image('https://i.ibb.co/GC8c367/Exporta-o.png')

        # Upload de arquivos
        uploaded_files = st.file_uploader(
            'Faça upload dos arquivos csv:',
            accept_multiple_files=True,
            type=['csv'],
            help='O upload dos arquivos deve ser feito exatamente como foram feitos os downloads do site.',
            key='files_export'
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
                    table_name = 'export_vinho'
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

    ### Upload de Dados de Importação ###
    with tab2:
        st.header('Importação de Vinhos')

        with st.expander('Modelos de Arquivos'):
            st.image('https://i.ibb.co/k5SGq8n/Importa-o.png')

        # Upload de arquivos
        uploaded_files = st.file_uploader(
            'Faça upload dos arquivos csv:',
            accept_multiple_files=True,
            type=['csv'],
            help='O upload dos arquivos deve ser feito exatamente como foram feitos os downloads do site.',
            key='files_import'
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
                    table_name = 'import_vinho'
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

    ### Upload de Dados de Importação ###
    with tab3:
        st.header('Comercialização de Produtos')

        with st.expander('Modelos de Arquivos'):
            st.image('https://i.ibb.co/PjR58r2/Comercio.png')

        # Upload de arquivos
        uploaded_files = st.file_uploader(
            'Faça upload dos arquivos csv:',
            accept_multiple_files=True,
            type=['csv'],
            help='O upload dos arquivos deve ser feito conforme o formato esperado.',
            key='files_comercializacao'
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
                    table_name = 'comercio_vinho'
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
        {datetime.now().year} - FIAP | PÓS TECH | Data Analytics | Tech Challenge - Cézar Maldini. Todos os direitos reservados.
    </footer>
""", unsafe_allow_html=True)