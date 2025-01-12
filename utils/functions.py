import streamlit as st
import time

# Função para formatar número em Mil, Milhões e Bilhões
def format_number(valor):
    for unidade in ['', 'Mil', 'Milhões', 'Bilhões']:
        if valor < 1000:
            return f'{valor:.2f} {unidade}'.strip()
        valor /= 1000
    return f'{valor:.2f} Trilhões'


@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()