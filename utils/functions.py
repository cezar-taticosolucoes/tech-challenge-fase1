# Função para formatar número em Mil, Milhões e Bilhões
def format_number(valor):
    for unidade in ['', 'Mil', 'Milhões', 'Bilhões']:
        if valor < 1000:
            return f'{valor:.2f} {unidade}'.strip()
        valor /= 1000
    return f'{valor:.2f} Trilhões'
