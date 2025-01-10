# Analytics | Vinhos 🍷

Este projeto é uma aplicação interativa desenvolvida com Streamlit para análise de dados relacionados à exportação, importação e comercialização de vinhos. A aplicação permite a manipulação de arquivos CSV, o processamento de dados, e o armazenamento em um banco de dados PostgreSQL hospedado na nuvem.

## Funcionalidades

### Navegação
A aplicação oferece uma barra lateral para navegar entre as seguintes seções:
- **Home**: Página inicial da aplicação.
- **Analytics**: Análise de dados sobre exportações de vinho.
- **Exportações**: Upload, processamento e armazenamento de dados de exportações.
- **Importações**: Upload, processamento e armazenamento de dados de importações.
- **Comercialização**: Upload, processamento e armazenamento de dados de comercialização.

### Detalhes das Funcionalidades

#### Analytics
- Exibição de dados agregados de exportações de vinho por país.
- Filtro dinâmico por país.
- Métricas detalhadas de quantidade total e valor total exportado.

#### Exportações, Importações e Comercialização
- Upload de arquivos CSV.
- Processamento de dados.
- Exibição dos dados processados.
- Armazenamento de dados no banco PostgreSQL, evitando duplicatas.

## Tecnologias Utilizadas

- **Linguagem**: Python
- **Frameworks**: 
  - [Streamlit](https://streamlit.io/): Para desenvolvimento da interface interativa.
  - [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu): Para navegação personalizada.
  - [streamlit-echarts](https://github.com/andfanilo/streamlit-echarts): Para gráficos interativos.
- **Banco de Dados**: PostgreSQL, acessado via [SQLAlchemy](https://www.sqlalchemy.org/).
- **Manipulação de Dados**: [Pandas](https://pandas.pydata.org/).

## Configuração do Projeto

### Pré-requisitos
- Python 3.8 ou superior
- Banco de dados PostgreSQL configurado
- Dependências listadas no arquivo `requirements.txt`

## Estrutura do Projeto
```
├── app.py                     # Arquivo principal da aplicação
├── utils/
│   ├── data_exportacao.py     # Processamento de dados de exportações
│   ├── data_importacao.py     # Processamento de dados de importações
│   └── data_comercio.py       # Processamento de dados de comercialização
├── requirements.txt           # Dependências do projeto
└── README.md                  # Documentação do projeto
```

## Créditos
- Desenvolvido por **Cézar Maldini**.