import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st

# Configurar a conexão com o banco de dados PostgreSQL
db_url = "postgresql://db_data_tech:dxNVQ2xbdjHmABoVE84CYMGnyo8EOasa@dpg-cu1qptpu0jms738l9cog-a.oregon-postgres.render.com/db_data_tech"
engine = create_engine(db_url)

# Título da página no Streamlit
st.title("Análise de Tendência e Previsão de Exportação de Vinhos")

# Consulta SQL para obter o ano mais recente
query_max_year = '''
SELECT MAX(CAST("Ano" AS INTEGER)) AS ano_mais_recente
FROM "export_vinho";
'''

# Executa a consulta para obter o ano mais recente
result = pd.read_sql(query_max_year, engine)

# Converte o ano mais recente para inteiro
ano_mais_recente = int(result.loc[0, 'ano_mais_recente']) if not result.empty else None

if ano_mais_recente:
    # Define o limite de anos baseado no ano mais recente
    ano_limite = ano_mais_recente - 15

    # Consulta SQL para buscar os últimos 15 anos
    query_export = f'''
    SELECT CAST("Ano" AS INTEGER) AS "Ano", SUM("Quantidade") as "Quantidade", SUM("Valor") as "Valor"
    FROM "export_vinho"
    WHERE CAST("Ano" AS INTEGER) >= {ano_limite}
    GROUP BY "Ano"
    ORDER BY "Ano";
    '''

    # Executa a consulta
    df = pd.read_sql(query_export, engine)

    if not df.empty:
        # Passo 3: Exibir os dados no Streamlit
        st.subheader("Dados Históricos")
        st.dataframe(df)

        # Passo 4: Modelagem e previsão
        def forecast_series(data, years, label):
            try:
                # Criar modelo de suavização exponencial
                model = ExponentialSmoothing(data, trend='add', seasonal=None)
                fit = model.fit()
                forecast = fit.forecast(5)  # Previsão para os próximos 5 anos

                # Preparar os dados para o gráfico
                fig = go.Figure()

                # Adicionar dados históricos
                fig.add_trace(go.Scatter(x=years, y=data, mode='lines+markers', name='Dados Históricos'))

                # Adicionar ajuste do modelo
                fig.add_trace(go.Scatter(x=years, y=fit.fittedvalues, mode='lines', name='Ajuste do Modelo', line=dict(color='green')))

                # Adicionar previsão
                future_years = np.arange(years.iloc[-1] + 1, years.iloc[-1] + 6)
                fig.add_trace(go.Scatter(x=future_years, y=forecast, mode='lines+markers', name='Previsão', line=dict(color='red')))

                # Configurar layout do gráfico
                fig.update_layout(
                    title=f'Tendência e Previsão: {label}',
                    xaxis_title='Ano',
                    yaxis_title=label,
                    template='plotly_white',
                    legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1)
                )

                # Retornar o gráfico
                return fig, forecast
            except Exception as e:
                st.error(f"Erro ao gerar previsão para {label}: {e}")
                return None, None

        # Previsão para Quantidade
        st.subheader("Previsão de Quantidade Exportada")
        fig_quantidade, forecast_quantidade = forecast_series(df['Quantidade'], df['Ano'], 'Quantidade Exportada')
        if fig_quantidade:
            st.plotly_chart(fig_quantidade)

        # Previsão para Valor
        st.subheader("Previsão de Valor Exportado")
        fig_valor, forecast_valor = forecast_series(df['Valor'], df['Ano'], 'Valor Exportado')
        if fig_valor:
            st.plotly_chart(fig_valor)

        # Exibir previsões futuras
        st.subheader("Previsões para os Próximos 5 Anos")
        st.write("Previsão para Quantidade (próximos 5 anos):")
        st.write(forecast_quantidade)
        st.write("Previsão para Valor (próximos 5 anos):")
        st.write(forecast_valor)
    else:
        st.warning("Nenhum dado encontrado para os últimos 15 anos.")
else:
    st.error("Não foi possível obter o ano mais recente no banco de dados.")