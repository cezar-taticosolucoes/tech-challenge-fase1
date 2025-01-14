import pandas as pd

# Função que executa uma query no Banco de Dados PostgreSQL e retorna o ano mais recente da tabela export_vinho
def get_recent_year_export(engine):
    query_max_year_export = '''
    SELECT MAX(CAST("Ano" AS INTEGER)) AS ano_mais_recente
    FROM export_vinho;
    '''
    result_export = pd.read_sql(query_max_year_export, engine)
    return int(result_export.loc[0, 'ano_mais_recente'])

# Função que executa uma query no Banco de Dados PostgreSQL e retorna os dados dos últimos 15 anos da tabela export_vinho
def get_last_15_years_data_export(engine):
    ano_mais_recente = get_recent_year_export(engine)
    ano_limite_export = ano_mais_recente - 15

    query_export = f'''
    SELECT *
    FROM export_vinho
    WHERE CAST("Ano" AS INTEGER) >= {ano_limite_export};
    '''
    df_export = pd.read_sql(query_export, engine).sort_values('Ano', ascending=True)
    df_export['Ano'] = df_export['Ano'].astype(int)
    return df_export

# Função que executa uma query no Banco de Dados PostgreSQL e retorna o ano mais recente da tabela import_vinho
def get_recent_year_import(engine):
    query_max_year_export = '''
    SELECT MAX(CAST("Ano" AS INTEGER)) AS ano_mais_recente
    FROM export_vinho;
    '''
    result_export = pd.read_sql(query_max_year_export, engine)
    return int(result_export.loc[0, 'ano_mais_recente'])

# Função que executa uma query no Banco de Dados PostgreSQL e retorna os dados dos últimos 15 anos da tabela import_vinho
def get_last_15_years_data_import(engine):
    ano_mais_recente_import = get_recent_year_import(engine)
    ano_limite_import = ano_mais_recente_import - 15

    query_import = f'''
    SELECT *
    FROM import_vinho
    WHERE CAST("Ano" AS INTEGER) >= {ano_limite_import};
    '''
    df_import = pd.read_sql(query_import, engine).sort_values('Ano', ascending=True)
    df_import['Ano'] = df_import['Ano'].astype(int)
    return df_import