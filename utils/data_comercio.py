import pandas as pd

def process_file_comercio(data):
    # Realizando a transformação inicial com melt
    data = data.melt(id_vars=['id', 'control', 'Produto'], var_name='Ano', value_name='Quantidade')
    
    # Coluna condicional
    data['Auxiliar'] = data['Produto'].apply(lambda x: 'sim' if x.isupper() else 'não')

    # Selecionar somente linhas com 'sim'
    data = data[data['Auxiliar'] == 'sim']

    # Remover colunas
    data = data.drop(columns=['Auxiliar', 'control']).drop_duplicates()

    # Remover linhas com Valor igual a zero
    data = data[~(data['Quantidade'] == 0)]

    # Aplicar o tipo float para a coluna 'Valor'
    data['Quantidade'] = data['Quantidade'].astype(float)

    return data