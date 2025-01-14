import streamlit as st
import time

# Função para formatar número em Mil, Milhões, Bilhões...
def format_number(valor):
    for unidade in ['', 'Mil', 'Milhões', 'Bilhões']:
        if valor < 1000:
            return f'{valor:.2f} {unidade}'.strip()
        valor /= 1000
    return f'{valor:.2f} Trilhões'

# Função para para fazer download das tabelas em formato csv
@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# Função para mensagem de sucesso do Download
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()