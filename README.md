# Analytics | Vinhos 🍷

Este projeto é uma aplicação interativa desenvolvida com Streamlit para análise de dados relacionados à exportação e importação de vinhos. A aplicação permite a manipulação de arquivos CSV, o processamento de dados, o armazenamento em um banco de dados PostgreSQL hospedado na nuvem e visualização dos dados por meio de gráficos e tabelas.

Ele permite visualizar informações detalhadas sobre os principais países, períodos analisados, e métricas relevantes como valor e quantidade exportados e importados.

## 📋 Funcionalidades

### Navegação
A aplicação oferece uma barra lateral para navegar entre as seguintes seções:
- **Analytics**: Análise de dados sobre exportações e importações de vinho.
- **Upload**: Upload de arquivos csv, processamento e armazenamento de dados de exportações e importações de vinho.

### Detalhes das Funcionalidades

#### Analytics
- Dashboards e Tabelas para análise de dados.
- Análise dos principais países conforme input do usuário.
- Filtros dinâmicos por país, tipos e período.
- Análises complementares.

#### Upload
- Sessão para adição de novos dados no Banco de Dados. 
- Upload de arquivos CSV.
- Processamento de dados.
- Exibição dos dados processados.
- Armazenamento de dados no banco PostgreSQL, evitando duplicatas.

![Upload](https://i.ibb.co/WfLxmdh/Data-Pipeline-Tech-Challenge.jpg)

## Tecnologias Utilizadas

- **Linguagem**: Python
- **Frameworks**: 
  - [Streamlit](https://streamlit.io/): Para desenvolvimento da interface interativa.
  - [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu): Para navegação personalizada.
- **Visualização de Dados**: 
  - [Plotly Express](https://plotly.com/python/plotly-express/): Para criação de gráficos interativos e personalizados.
- **Banco de Dados**: PostgreSQL, acessado via [SQLAlchemy](https://www.sqlalchemy.org/).
- **Manipulação de Dados**: [Pandas](https://pandas.pydata.org/).

![Tecnologias](https://i.ibb.co/8DgtXxW/Tecnologias-App-Tech-Challenge.png)

## Configuração do Projeto

### Pré-requisitos
- Python 3.8 ou superior
- Banco de dados PostgreSQL configurado
- Dependências listadas no arquivo `requirements.txt`

## Estrutura do Projeto
```
├── .streamlit/
│   └── config.toml
├── .venv/                     # Ambiente virtual
├── utils/                     # Módulo utilitário
│   ├── __pycache__/           # Arquivos compilados em bytecode
│   ├── db_queries.py          # Script para consultas ao banco de dados
│   ├── functions.py           # Funções gerais e utilitárias
│   ├── pipeline_comercio.py   # Pipeline relacionado ao comércio
│   ├── pipeline_export.py     # Pipeline para exportação
│   └── pipeline_import.py     # Pipeline para importação
├── .gitignore                 # Arquivo para ignorar arquivos/pastas no Git
├── app.py                     # Arquivo principal da aplicação Streamlit
├── README.md                  # Documentação do projeto
└── requirements.txt           # Dependências do projeto
```

## Créditos
- Desenvolvido por **Cézar Maldini**.