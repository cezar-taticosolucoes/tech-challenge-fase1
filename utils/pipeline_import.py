import pandas as pd

def process_file_import(file_name, data):
    # Transposição das colunas de Anos em linhas
    data = data.melt(id_vars=['Id', 'País'], var_name='Ano', value_name='Value')

    # Colunas de Valor e Quantidade
    data['Valor'] = data.apply(lambda row: row['Value'] if '.' in str(row['Ano']) else None, axis=1)
    data['Quantidade'] = data.apply(lambda row: row['Value'] if '.' not in str(row['Ano']) else None, axis=1)

    # Removendo o '.1' da coluna 'Ano'
    data['Ano'] = data['Ano'].str.replace(r'\.1$', '', regex=True)

    # Groupby por 'Id', 'País' e 'Ano' e somando as colunas 'Quantidade' e 'Valor'
    data = data.groupby(['Id', 'País', 'Ano'], as_index=False).agg({
        'Quantidade': 'sum',
        'Valor': 'sum'
    })

    # Adicionando a nova coluna 'Tipo' com base no nome do arquivo
    if file_name == 'ImpVinhos.csv':
        data['Tipo'] = 'Vinhos de mesa'
    elif file_name == 'ImpEspumantes.csv':
        data['Tipo'] = 'Espumantes'
    elif file_name == 'ImpFrescas.csv':
        data['Tipo'] = 'Uvas frescas'
    elif file_name == 'ImpPassas.csv':
        data['Tipo'] = 'Uvas passas'
    elif file_name == 'ImpSuco.csv':
        data['Tipo'] = 'Suco de uva'
    else:
        data['Tipo'] = 'Desconhecido'

    # Removendo linhas com Quantidade e Valor iguais a zero
    data = data[~((data['Quantidade'] == 0) & (data['Valor'] == 0))]

    return data