# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral

Este é um sistema de gerenciamento de checklists no Trello para acompanhamento da entrega de documentos de pessoas convocadas em concursos públicos da Prefeitura de Mogi das Cruzes. A aplicação é construída com Python e Streamlit, seguindo os princípios de Clean Architecture (arquitetura hexagonal).

## Comandos Comuns

### Executar a Aplicação
```bash
# Modo desenvolvimento (local)
streamlit run streamlit_app.py

# Usando Docker Compose
docker-compose up --build

# Criar um novo usuário
python create_user.py admin  # Cria usuário admin
python create_user.py        # Modo interativo
```

### Dependências e Ambiente
```bash
# Instalar dependências
pip install -r requirements.txt

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source .venv/bin/activate
```

### Migrações de Banco de Dados
```bash
# Criar nova migração
alembic revision --autogenerate -m "descricao da migration"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

## Arquitetura

### Estrutura em Camadas
O projeto segue uma arquitetura limpa com separação clara de responsabilidades:

```
src/
├── core/                    # Domínio e casos de uso (camada de negócio)
│   ├── candidate/          # Entidade Candidate e seus use cases
│   ├── convocation/        # Entidade Convocation e criação de checklists
│   ├── user/               # Entidade User e autenticação
│   └── shared/             # Classes base compartilhadas
│       ├── entity.py       # Classe base Entity (todos os modelos herdam dela)
│       ├── repository.py   # Protocolo Repository (interface base)
│       ├── usecase.py      # Protocolo UseCase (interface base)
│       ├── application.py  # Classe Result (retorno padronizado)
│       └── logger.py       # Logger segregado por tipo (info, warning, error, success)
├── adapters/               # Controladores e helpers de apresentação
│   ├── controller.py       # Controller genérico com introspecção
│   └── viewhelper.py       # Helper para criar views a partir de Results
└── external/               # Camada externa (persistência e páginas)
    ├── persistence/        # Implementações de repositories
    │   ├── trello/        # Adaptador Trello API
    │   ├── redis/         # Adaptador Redis
    │   └── sqlalchemyorm/ # Adaptador SQL (quando implementado)
    └── app_pages/         # Páginas Streamlit
```

### Padrões Arquiteturais

**Auto-descoberta de Use Cases e Repositories:**
- O `src/core/__init__.py` descobre automaticamente todos os use cases decorados com `@usecase_map`
- O `src/external/persistence/__init__.py` descobre repositories decorados com `@repository_map`
- Repositories são carregados com base na variável de ambiente `DB_FRAMEWORK`

**Controller Genérico:**
- `Controller` usa introspecção para identificar dependências de use cases e repositories
- Injeta automaticamente o repository correto no use case baseado nas type hints
- Parseia requests e cria entidades automaticamente usando `GenericViewHelper`

**Resultado Padronizado:**
- Todos os use cases retornam um objeto `Result` com listas segregadas por tipo:
  - `error_msg`: Mensagens de erro
  - `warning_msg`: Mensagens de aviso
  - `info_msg`: Mensagens informativas
  - `success_msg`: Mensagens de sucesso
  - `entities`: Lista de entidades processadas
  - `objects`: Lista de objetos adicionais

### Criar Novos Use Cases

```python
# src/core/{domínio}/service/{nome_usecase}.py
from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result

@usecase_map('/path/do/recurso')
class MeuUseCase(UseCase):
    def __init__(self, repository: MeuRepository):
        self.repository = repository

    def execute(self, entity: MinhaEntidade) -> Result:
        result = Result()

        # Sua lógica aqui
        result.success_msg = "Operação realizada com sucesso"

        return result
```

### Criar Novos Repositories

```python
# src/external/persistence/{framework}/{nome}_repository.py
from src.external.persistence import repository_map
from src.core.candidate import CandidateRepository

@repository_map
class MeuRepository(CandidateRepository):
    def registry(self, entity):
        # Implementação
        pass

    def get_all(self, entity):
        pass

    def update(self, entity):
        pass

    def find_by_field(self, entity):
        pass

    def get_by_id(self, entity):
        pass

    def remove(self, entity):
        pass
```

## Configuração

### Variáveis de Ambiente
O projeto usa variáveis de ambiente para configuração. As credenciais podem ser fornecidas via:

1. Arquivo `.env` (modo desenvolvimento)
2. Streamlit Secrets (`.streamlit/secrets.toml` para produção)

**Variáveis necessárias:**
- `DATABASE_URL`, `DB_DATABASE`, `DB_DIALECT`, `DB_HOST`, `DB_PASSWORD`, `DB_PORT`, `DB_SCHEMA`, `DB_USER`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_USERNAME`
- `KEY_TRELLO`, `TOKEN_TRELLO`
- `FRAMEWORK_NAME`: Define se usa Streamlit ou carrega de env vars
- `DB_FRAMEWORK`: Define qual framework de persistência usar ('trello', 'sqlalchemyorm', 'redis')

### Framework de Persistência
O suporte a diferentes frameworks de persistência é selecionado via `DB_FRAMEWORK`:
- `'trello'`: Usa API do Trello para criar cards e checklists
- `'redis'`: Usa Redis para cache e persistência
- `'sqlalchemyorm'`: Usa banco de dados relacional (PostgreSQL/MySQL/SQLite)

## Integração Trello

O sistema cria automaticamente cards no Trello com checklists para cada candidato. Os cards incluem:
- Nome do candidato com classificação e cargo
- Descrição template com dados da convocação
- Labels baseadas no edital
- Datas de início e prazo

**IDs importantes (configurados em `TrelloConvocationRepository`):**
- `id_list`: ID da lista onde os cards são criados
- `id_card_source`: Card template usado para clonagem
- `id_card_label`: Card usado para obter labels disponíveis
- `id_board`: ID do board principal

## Autenticação

O sistema usa `streamlit-authenticator` com suporte a:
- Login/logout de usuários
- Gerenciamento de usuários via página `/user/registry`
- Role-based access (admin vê páginas adicionais)

Para criar usuários, use o script `create_user.py`.

## Páginas Streamlit

As páginas são organizadas em `src/external/app_pages/`:
- Página principal: Lista de candidatos com checklists
- Authentication Manager: Gerenciamento de usuários (apenas admin)

Use o decorador `add_page_title()` e `show_pages()` para navegação.

## Testes

O projeto não possui testes implementados ainda. Considerar adicionar testes unitários para:
- Use cases
- Repositories
- Entidades
- Páginas Streamlit

## Notas Importantes

1. **Mensagens Segregadas**: Sempre use o tipo correto de mensagem no `Result` (error, warning, info, success) para melhor UX
2. **Validação**: Use o método `validate_data()` das entidades antes de processar
3. **Tratamento de Erros**: Use try/except em use cases e adicione mensagens apropriadas ao `Result`
4. **Reflection**: O controller usa type hints para injetar dependências, mantenha as anotações de tipo corretas
5. **Naming**: Use nomes descritivos para use cases e seguindo o padrão `{Entidade}{Acao}`
