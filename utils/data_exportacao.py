import pandas as pd

def process_file(file_name, data):
    # Realizando a transformação inicial com melt
    data = data.melt(id_vars=['Id', 'País'], var_name='Ano', value_name='Value')

    # Criando as novas colunas com base na condição
    data['Valor'] = data.apply(lambda row: row['Value'] if '.' in str(row['Ano']) else None, axis=1)
    data['Quantidade'] = data.apply(lambda row: row['Value'] if '.' not in str(row['Ano']) else None, axis=1)

    # Removendo o '.1' da coluna 'Ano'
    data['Ano'] = data['Ano'].str.replace(r'\.1$', '', regex=True)

    # Agrupando por 'Id', 'País' e 'Ano' e somando as colunas 'Quantidade' e 'Valor'
    data = data.groupby(['Id', 'País', 'Ano'], as_index=False).agg({
        'Quantidade': 'sum',
        'Valor': 'sum'
    })

    # Adicionando a nova coluna 'Tipo' com base no nome do arquivo
    if file_name == 'ExpVinho.csv':
        data['Tipo'] = 'Vinhos de mesa'
    elif file_name == 'ExpEspumantes.csv':
        data['Tipo'] = 'Espumantes'
    elif file_name == 'ExpUva.csv':
        data['Tipo'] = 'Uvas frescas'
    elif file_name == 'ExpSuco.csv':
        data['Tipo'] = 'Suco de uva'
    else:
        data['Tipo'] = 'Desconhecido'

    # Removendo linhas com Quantidade e Valor iguais a zero
    data = data[~((data['Quantidade'] == 0) & (data['Valor'] == 0))]

    return data