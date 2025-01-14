# Import de bibliotecas do Streamlit
import streamlit as st
import streamlit_option_menu
from streamlit_option_menu import option_menu

# Import de Funções da Pasta utils/
from utils.pipeline_export import process_file
from utils.pipeline_import import process_file_import
from utils.functions import format_number, converte_csv, mensagem_sucesso
from utils.db_queries import get_last_15_years_data_export, get_last_15_years_data_import

# Outras bibliotecas
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import time
import pandas as pd
import plotly.express as px

# Configuração inicial do App
st.set_page_config(
    page_title='Analytics | Vinhos',
    page_icon='🍷',
    layout='wide'
)

# Navegação do App
with st.sidebar:
    option = option_menu(
        menu_title="Navegação",
        options=["Analytics", "Upload"],
        icons=["bar-chart", "arrow-up-square"],
        menu_icon="card-list",
        default_index=0
    )

# Configuração do Banco de Dados PostgreSQl
db_url = st.secrets["DB_URL"]
engine = create_engine(db_url)


# Consulta SQL Tabela: export_vinho
df_export = get_last_15_years_data_export(engine)

# Consulta SQL Tabela: import_vinho
df_import = get_last_15_years_data_import(engine)

### Página Analytics ###
if option == 'Analytics':
    st.title('Data Analytics')

    ### Abas: Exportação e Importação ###
    tab1, tab2 = st.tabs(['Exportação', 'Importação'])

    ### Analytics Exportação ###
    with tab1:       
        sub_tab1, sub_tab2 = st.tabs(['Dashboard 📊', 'Tabela 🗂️'])

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
                        # Filtro de Tipos
                        tipos_disponiveis = df_export['Tipo'].dropna().unique()
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
                
                # Aplicar filtros no DataFrame: df_export
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

                # Groupby dos dados por Ano e País
                df_export_agg = (
                    df_filtered.groupby(['Ano', 'País'], as_index=False)['Valor']
                    .sum()
                )

                # Ano de início e ano final de análise
                start_year, end_year = year

                # Subtítulo do dashboard
                st.markdown(
                    f"""
                    <h3> Análise de Exportação de Vinhos: 
                    <span style="color:#F1145C;">Top {number_paises} Países</span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

                # País de Origem
                st.markdown(
                    f"""
                    <p style="font-size:20px;">País de Origem: 
                    <span style="color:#F1145C;">Brasil</span></p>
                    """,
                    unsafe_allow_html=True
                )

                # Período Analisado
                st.markdown(
                    f"""
                    <p style="font-size:18px;">Período Analisado: 
                    <span style="color:#F1145C;">{start_year} - {end_year}</span></p>
                    """,
                    unsafe_allow_html=True
                )

                #### Criação dos Gráficos ####
                # Gráfico de barras: Valor
                df_valor_pais = (
                    df_filtered.groupby('País', as_index=False)['Valor']
                    .sum()
                    .nlargest(number_paises, 'Valor')
                )

                # Ordemm com base no valor
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

                # Gráfico de barras: Quantidade
                df_quant_pais = (
                    df_filtered.groupby('País', as_index=False)['Quantidade']
                    .sum()
                    .nlargest(number_paises, 'Quantidade')
                )

                # Ordem com base na quantidade
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

                # Gráfico de linhas: Valor por Ano
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

                # Exibição dos Gráficos
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f'💵 Valor Total (US$): Top {number_paises} Países', format_number(df_valor_pais['Valor'].sum()))
                    st.plotly_chart(fig_valor_pais, use_container_width=True)
                with col2:
                    st.metric(f'🍷 Quantidade Total (L): Top {number_paises} Países', format_number(df_quant_pais['Quantidade'].sum()))
                    st.plotly_chart(fig_quant_pais, use_container_width=True)

                st.plotly_chart(fig_valor_ano_pais, use_container_width=True)

                st.divider()

                # Sessão para Análises Complementares
                st.markdown(
                    f"""
                    <h4>Análises Complementares</h4>
                    """,
                    unsafe_allow_html=True
                )

                # Análise do Custo Unitário Médio Total de Exportação de Vinho
                if not df_export.empty:
                    df_export_valid = df_export[df_export['Quantidade'] > 0].copy()
                    df_export_valid['Custo Unitário Médio'] = df_export_valid['Valor'] / df_export_valid['Quantidade']

                    # Custo unitário médio total
                    custo_unitario_medio_total = (
                        df_export_valid['Valor'].sum() / df_export_valid['Quantidade'].sum()
                        if df_export_valid['Quantidade'].sum() > 0 else 0
                    )

                    # Custo unitário médio por tipo
                    custo_unitario_por_tipo = (
                        df_export_valid.groupby('Tipo', as_index=False)
                        .apply(lambda x: (x['Valor'].sum() / x['Quantidade'].sum()) if x['Quantidade'].sum() > 0 else 0)
                    )
                    custo_unitario_por_tipo.columns = ['Tipo', 'Custo Unitário Médio']

                    # Exibição dos resultados
                    st.expander("Custo Unitário Médio Total de Exportação de Vinho (US$/L)").markdown(
                        f"""
                        **Custo Unitário Médio Total de Exportação de Vinho (US$/L):** 
                        {custo_unitario_medio_total:,.2f} 
                        """
                    )

                    st.expander("Custo Unitário Médio por Tipo de Vinho (US$/L)").markdown(
                        "\n".join([f"- **{row['Tipo']}:** {row['Custo Unitário Médio']:,.2f} US$/L" for _, row in custo_unitario_por_tipo.iterrows()])
                    )
                else:
                    st.warning("Não há dados disponíveis para realizar esta análise.")

                # Análise do Pico de Exportação
                df_export_valid['Ano'] = df_export_valid['Ano'].astype(int)
                pico_exportacao = (
                    df_export_valid.groupby(['País', 'Ano'])[['Valor', 'Quantidade']]
                    .sum()
                    .reset_index()
                    .sort_values(by='Valor', ascending=False)
                    .iloc[0]
                )
                pais_pico = pico_exportacao['País']
                ano_pico = pico_exportacao['Ano']
                valor_pico = pico_exportacao['Valor']
                quantidade_pico = pico_exportacao['Quantidade']

                # Custo unitário no ano de pico
                custo_unitario_pico = valor_pico / quantidade_pico

                # Custo unitário no ano anterior
                df_ano_anterior = df_export_valid[(df_export_valid['País'] == pais_pico) & (df_export_valid['Ano'] == (ano_pico - 1))]
                if not df_ano_anterior.empty:
                    valor_ano_anterior = df_ano_anterior['Valor'].sum()
                    quantidade_ano_anterior = df_ano_anterior['Quantidade'].sum()
                    custo_unitario_ano_anterior = valor_ano_anterior / quantidade_ano_anterior
                else:
                    custo_unitario_ano_anterior = None

                # Explicação do Pico
                explicacao_pico = (
                    f"O país **{pais_pico}** registrou o maior pico de exportação de vinho no ano **{ano_pico}**, com um valor total exportado de **{valor_pico:,.2f}** e um volume de **{quantidade_pico:,.2f}** litros. O custo unitário médio no ano de pico foi **{custo_unitario_pico:,.2f}**."
                )

                # Comparação com o ano anterior
                if custo_unitario_ano_anterior is not None:
                    explicacao_pico += (
                        f" No ano anterior (**{ano_pico - 1}**), o custo unitário médio foi **{custo_unitario_ano_anterior:,.2f}**. "
                    )
                    if custo_unitario_pico > custo_unitario_ano_anterior:
                        explicacao_pico += (
                            "O aumento no custo unitário médio pode indicar uma exportação de vinhos de maior valor agregado no ano do pico."
                        )
                    elif custo_unitario_pico < custo_unitario_ano_anterior:
                        explicacao_pico += (
                            "A redução no custo unitário médio sugere que o aumento no valor exportado foi impulsionado principalmente pelo volume."
                        )
                else:
                    explicacao_pico += (
                        f" Não há dados disponíveis para o ano anterior (**{ano_pico - 1}**) para comparação."
                    )

                # Exibição dos resultados
                st.expander("Análise de Pico de Exportação").markdown(explicacao_pico)

                # Análise dos 3 Principais Exportadores de Vinho do Brasil nos Últimos 5 Anos
                df_export_valid_ultimos_5_anos = df_export_valid[df_export_valid['Ano'] >= (df_export_valid['Ano'].max() - 5)]
                top_3_exportadores = (
                    df_export_valid_ultimos_5_anos.groupby('País')
                    .agg({'Valor': 'sum', 'Quantidade': 'sum'})
                    .reset_index()
                    .sort_values(by='Valor', ascending=False)
                    .head(3)
                )

                # Exibição do Top 3 Exportadores
                with st.expander("Top 3 Exportadores de Vinho do Brasil nos Últimos 5 Anos"):
                    st.markdown("**Top 3 Exportadores de Vinho do Brasil nos Últimos 5 Anos:**")
                    for _, row in top_3_exportadores.iterrows():
                        st.markdown(
                            f"- **{row['País']}:** Valor exportado: **{row['Valor']:,.2f}**, Quantidade exportada: **{row['Quantidade']:,.2f}** litros"
                        )

                    # Custo unitário médio total dos últimos 5 anos para os 3 principais exportadores
                    st.markdown("**Análise do Custo Unitário Médio dos 3 Principais Exportadores nos Últimos 5 Anos:**")
                    for _, row in top_3_exportadores.iterrows():
                        df_export_pais = df_export_valid_ultimos_5_anos[df_export_valid_ultimos_5_anos['País'] == row['País']]
                        custo_unitario_pais = df_export_pais['Valor'].sum() / df_export_pais['Quantidade'].sum() if df_export_pais['Quantidade'].sum() > 0 else 0

                        st.markdown(f"**{row['País']}:**")
                        st.markdown(f"  - **Custo Unitário Médio Total (últimos 5 anos):** {custo_unitario_pais:,.2f} US$/L")           

        # Exportação: Sessão Tables
        with sub_tab2:
            # Filtros
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

            # Aplicando os filtros no DataFrame: df_export
            df_filtrado = df_export.copy()

            if pais:
                df_filtrado = df_filtrado[df_filtrado['País'].isin(pais)]
            if tipo:
                df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipo)]
            if year:
                df_filtrado = df_filtrado[
                    (df_filtrado['Ano'] >= year[0]) & (df_filtrado['Ano'] <= year[1])
                ]

            # Ano de início e ano final de análise
            start_year, end_year = year

            # Subtítulo do dashboard
            st.markdown(
                    f"""
                    <h3> Análise de Exportação de Vinhos:
                    <span style="color:#F1145C;"></span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

            # País de origem
            st.markdown(
                    f"""
                    <p style="font-size:20px;">País de Origem: 
                    <span style="color:#F1145C;">Brasil</span></p>
                    """,
                    unsafe_allow_html=True
                )

            # Período Analisado
            st.markdown(
                    f"""
                    <p style="font-size:18px;">Período Analisado: 
                    <span style="color:#F1145C;">{start_year} - {end_year}</span></p>
                    """,
                    unsafe_allow_html=True
                )    

            # Valor Total e Quantidade Total
            total_quantity = df_filtrado["Quantidade"].sum()
            total_value = df_filtrado["Valor"].sum()

            # Formatação Valor Total e Quantidade Total
            quantidade_formatada = format_number(total_quantity)
            valor_formatado = format_number(total_value)

            # Exibição dos Valores Totais
            col1, col2 = st.columns(2)
            with col1:
                col1.metric("💵 Valor Total (US$)", valor_formatado)
            with col2:
                col2.metric("🍷 Quantidade Total (L)", quantidade_formatada)

            # Exibição da tabela
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
            
            # Número de linhas da tabela (Dinâmico a partir dos filtros aplicados)
            st.markdown(
                f"""
                <p>A tabela possui <span style="color:#F1145C;">{df_filtrado.shape[0]}</span> linhas.
                """, 
                unsafe_allow_html=True
            )
            
            # Download da tabela em formato csv
            st.markdown('Escreva um nome para o arquivo')
            coluna1, coluna2 = st.columns(2)
            with coluna1:
                nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
                nome_arquivo += '.csv'
            with coluna2:
                st.download_button('Download', data = converte_csv(df_filtrado), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso, help='Clique para fazer download dos dados em formato csv.')

    ### Analytics Importações ###
    with tab2:
        sub_tab1, sub_tab2 = st.tabs(['Dashboard 📊', 'Tabela 🗂️'])

        ### Importação: Dashboard
        with sub_tab1:
            with st.container():
                # Filtros
                with st.expander('Filtros'):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # Filtro Número de Países
                        number_paises_import = st.number_input('Número de países a serem análisados', min_value=2, max_value=15, value=5, help='Selecionar o número de Países que serão análisados: de 2 a 15.',key='number_paises_import')
                    with col2:
                        # Filtro de Tipos
                        tipos_disponiveis_import = df_import['Tipo'].dropna().unique()
                        tipo_selecionado_import = st.multiselect(
                            "Selecione o(s) Tipo(s):",
                            options=tipos_disponiveis_import,
                            default=tipos_disponiveis_import,
                            key='tipo_selecionado_import'
                        )
                    with col3:
                        # Filtro de Período
                        year_import = st.slider(
                            "Selecione um Período de Anos",
                            df_import['Ano'].min(),
                            df_import['Ano'].max(),
                            (df_import['Ano'].min(), df_import['Ano'].max()),
                            key="year_import"
                        )
                
                # Aplicar filtros no DataFrame: df_import
                df_filtered_import = df_import[
                    (df_import['Ano'] >= year_import[0]) & 
                    (df_import['Ano'] <= year_import[1]) &
                    (df_import['Tipo'].isin(tipo_selecionado_import))
                ]

                # Filtrar os países com maior valor dentro do intervalo e tipo selecionados
                top_countries_import = (
                    df_filtered_import.groupby('País')['Valor']
                    .sum()
                    .nlargest(number_paises_import)
                    .index
                )
                df_filtered_import = df_filtered_import[df_filtered_import['País'].isin(top_countries_import)]

                # Groupby dos dados por Ano e País
                df_import_agg = (
                    df_filtered_import.groupby(['Ano', 'País'], as_index=False)['Valor']
                    .sum()
                )

                # Ano de início e ano final de análise
                start_year_import, end_year_import = year_import

                # Subtítulo do dashboard
                st.markdown(
                    f"""
                    <h3> Análise de Importação de Vinhos:
                    <span style="color:#F1145C;">Top {number_paises_import} Países</span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

                # País de origem
                st.markdown(
                    f"""
                    <p style="font-size:20px;">País de Origem: 
                    <span style="color:#F1145C;">Brasil</span></p>
                    """,
                    unsafe_allow_html=True
                )

                # Período analisado
                st.markdown(
                    f"""
                    <p style="font-size:18px;">Período Analisado: 
                    <span style="color:#F1145C;">{start_year_import} - {end_year_import}</span></p>
                    """,
                    unsafe_allow_html=True
                )

                #### Criação dos Gráficos ####
                # Gráfico de barras: Valor
                df_valor_pais_import = (
                    df_filtered_import.groupby('País', as_index=False)['Valor']
                    .sum()
                    .nlargest(number_paises_import, 'Valor')
                )

                # Ordem por valor
                country_order_valor_import = df_valor_pais_import.sort_values('Valor', ascending=False)['País'].tolist()

                fig_valor_pais_import = px.bar(
                    df_valor_pais_import,
                    x='Valor',
                    y='País',
                    text_auto='.2s',
                    title=f"Valor (US$): Top {number_paises_import} Países",
                    color_discrete_sequence=['#F1145C'],
                    category_orders={"País": country_order_valor_import},
                    hover_data={'País': True, 'Valor': ':.2f'},
                    height=500 + (number_paises_import - 5) * 50
                )

                # Gráfico de barras: Quantidade
                df_quant_pais_import = (
                    df_filtered_import.groupby('País', as_index=False)['Quantidade']
                    .sum()
                    .nlargest(number_paises_import, 'Quantidade')
                )

                # Ordem por quantidade
                country_order_quant_import = df_quant_pais_import.sort_values('Quantidade', ascending=False)['País'].tolist()

                fig_quant_pais_import = px.bar(
                    df_quant_pais_import,
                    x='Quantidade',
                    y='País',
                    text_auto='.2s',
                    title=f"Quantidade Total (L): Top {number_paises_import} Países",
                    color_discrete_sequence=['#F1145C'],
                    category_orders={"País": country_order_quant_import},
                    hover_data={'País': True, 'Quantidade': ':.2f'},
                    height=500 + (number_paises_import - 5) * 50
                )

                # Gráfico de linhas: Valor por Ano
                fig_valor_ano_pais_import = px.line(
                    df_import_agg,
                    x='Ano',
                    y='Valor',
                    color='País',
                    range_y=(df_import_agg['Valor'].min() - 1000000, df_import_agg['Valor'].max() + 1000000),
                    markers=True,
                    title=f"Valor por Ano (US$): Top {number_paises_import} Países",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    hover_data={'Ano': True, 'Valor': ':.2f'}
                )

                # Exibição dos gráficos
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f'💵 Valor Total (US$): Top {number_paises_import} Países', format_number(df_valor_pais_import['Valor'].sum()))
                    st.plotly_chart(fig_valor_pais_import, use_container_width=True)
                with col2:
                    st.metric(f'🍷 Quantidade Total (L): Top {number_paises_import} Países', format_number(df_quant_pais_import['Quantidade'].sum()))
                    st.plotly_chart(fig_quant_pais_import, use_container_width=True)

                st.plotly_chart(fig_valor_ano_pais_import, use_container_width=True)
        
        ### Importação: Tabelas
        with sub_tab2:
            # Filtros
            with st.expander('Filtros'):
                col1, col2, col3 = st.columns(3)
                with col1:
                    pais_import = st.multiselect('Selecione um país', pd.Series(df_import['País'].unique()).sort_values(ascending=True), key='pais_import')
                with col2:
                    tipo_import = st.multiselect('Selecione os tipos', pd.Series(df_import['Tipo'].unique()).sort_values(ascending=True), key='tipo_import')
                with col3:
                    year_import = st.slider('Selecione um Período de Anos', 
                                    df_import['Ano'].min(), 
                                    df_import['Ano'].max(), 
                                    (df_import['Ano'].min(), df_import['Ano'].max()),
                                    key='import_year')
                    
            # Aplicando os filtros no DataFrame: df_import
            df_filtrado_import = df_import.copy()

            if pais_import:
                df_filtrado_import = df_filtrado_import[df_filtrado_import['País'].isin(pais_import)]
            if tipo_import:
                df_filtrado_import = df_filtrado_import[df_filtrado_import['Tipo'].isin(tipo_import)]
            if year_import:
                df_filtrado_import = df_filtrado_import[
                    (df_filtrado_import['Ano'] >= year_import[0]) & (df_filtrado_import['Ano'] <= year_import[1])
                ]

            # AAno de início e ano final de análise
            start_year_import, end_year_import = year_import

            # Subtítulo do dashboard
            st.markdown(
                    f"""
                    <h3> Análise de Importação de Vinhos
                    <span style="color:#F1145C;"></span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

            # País de origem
            st.markdown(
                    f"""
                    <p style="font-size:20px;">País de Origem: 
                    <span style="color:#F1145C;">Brasil</span></p>
                    """,
                    unsafe_allow_html=True
                )

            # Período analisado
            st.markdown(
                    f"""
                    <p style="font-size:18px;">Período Analisado: 
                    <span style="color:#F1145C;">{start_year_import} - {end_year_import}</span></p>
                    """,
                    unsafe_allow_html=True
                ) 

            # Valor Total e Quantidade Total
            total_quantity_import = df_filtrado_import["Quantidade"].sum()
            total_value_import = df_filtrado_import["Valor"].sum()

            # Formato Valor Total e Quantidade Total
            quantidade_formatada_import = format_number(total_quantity_import)
            valor_formatado_import = format_number(total_value_import)

            # Exibição Valor Total e Quantidade Total
            col1, col2 = st.columns(2)
            with col1:
                col1.metric("💵 Valor Total (US$)", valor_formatado_import)
            with col2:
                col2.metric("🍷 Quantidade Total (L)", quantidade_formatada_import)

            # Exibição da tabela
            if not df_filtrado_import.empty:
                st.dataframe(
                    df_filtrado_import,
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
            
            # Número de linhas da tabela
            st.markdown(
                f"""
                <p>A tabela possui <span style="color:#F1145C;">{df_filtrado_import.shape[0]}</span> linhas.
                """, 
                unsafe_allow_html=True
            )

            # Download da tabela em formato csv
            st.markdown('Escreva um nome para o arquivo')
            coluna1, coluna2 = st.columns(2)
            with coluna1:
                nome_arquivo_import = st.text_input('', label_visibility = 'collapsed', value = 'dados', key='nome_arquivo_import')
                nome_arquivo_import += '.csv'
            with coluna2:
                st.download_button('Download', data = converte_csv(df_filtrado_import), file_name = nome_arquivo_import, mime = 'text/csv', on_click = mensagem_sucesso, help='Clique para fazer download dos dados em formato csv.', key='download_import')
### Página Upload ###
elif option == 'Upload':
    st.title('Upload de Dados')
    # Explicação do Processo
    with st.expander('Processamento dos Dados'):
        st.markdown("""
        **Essa sessão deve ser utilizada somente para a adição de novos dados no Banco de Dados para serem utilizados no módulo de Analytics.**
        1. **Download dos arquivos CSV no site:**
        - Acesse o site [VITIBRASIL - Embrapa](http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_01) e faça o download dos arquivos CSV desejados.

        2. **Upload dos arquivos no app:**
        - Utilize o botão abaixo para fazer o upload dos arquivos CSV no aplicativo.

        3. **Tratamento e armazenamento no Banco de Dados PostgreSQL:**
        - O aplicativo irá processar os arquivos CSV e armazená-los no Banco de Dados PostgreSQL para a utilização no módulo de Analytics.
        """)

        st.image('https://i.ibb.co/WfLxmdh/Data-Pipeline-Tech-Challenge.jpg')

    # Abas: Exportação e Importação
    tab1, tab2 = st.tabs(['Exportações', 'Importações'])

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
        
        # Processamento dos dados
        if uploaded_files:
            consolidated_data = pd.DataFrame()

            for uploaded_file in uploaded_files:
                # Carregar o arquivo em um DataFrame
                df = pd.read_csv(uploaded_file, sep=';')

                # Processar o DataFrame usando o arquivo utilizando 'pipeline_export.py'
                processed_data = process_file(uploaded_file.name, df)

                # Concatenar o DataFrame
                consolidated_data = pd.concat(
                    [consolidated_data, processed_data], ignore_index=True)

            # Exibir os dados
            st.write('Dados processados:')
            st.dataframe(
                consolidated_data,
                width=2000,
                hide_index=True,
                column_config={
                    'Quantidade': st.column_config.NumberColumn('Quantidade (Kg)', format="%.2f"),
                    'Valor': st.column_config.NumberColumn('Valor (US$)', format="%.2f")
                }
            )

            # Botão para salvar os dados no banco de dados PostgreSQL
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

        # Processamento dos dados
        if uploaded_files:
            consolidated_data = pd.DataFrame()

            for uploaded_file in uploaded_files:
                # Carregar o arquivo em um DataFrame
                df = pd.read_csv(uploaded_file, sep=';')

                # Processar o DataFrame usando o arquivo `pipeline_import.py`
                processed_data = process_file_import(uploaded_file.name, df)

                # Concatenar o DataFrame
                consolidated_data = pd.concat(
                    [consolidated_data, processed_data], ignore_index=True)

            # Exibir os dados
            st.write('Dados processados:')
            st.dataframe(
                consolidated_data,
                width=2000,
                hide_index=True,
                column_config={
                    'Quantidade': st.column_config.NumberColumn('Quantidade (Kg)', format="%.2f"),
                    'Valor': st.column_config.NumberColumn('Valor (US$)', format="%.2f")
                }
            )

            # Botão para salvar os dados no banco de dados
            if st.button('Salvar dados no banco de dados', key='salve_import'):
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

# Rodapé
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