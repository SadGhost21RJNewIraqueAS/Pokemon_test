# Pokédex Digital API

API REST desenvolvida com FastAPI para gerenciar espécies de Pokémon, capturas, favoritos, propostas de alteração, autenticação e relatórios.

## Responsabilidades do projeto

| Pessoa | Perfil | Responsabilidades |
|---|---|---|
| Pessoa 1 | **Treinador** | Registrar capturas, marcar favoritos, comparar Pokémon, consultar a Pokédex pessoal e acompanhar evoluções. |
| Pessoa 2 | **Pesquisador** | Cadastrar espécies, registrar evoluções e enviar propostas de alteração. |
| Pessoa 3 | **Administrador** | Aprovar ou rejeitar propostas, editar ou remover registros, consultar relatórios e acessar a auditoria. |
| Pessoa 4 | **Autenticação / Usuários** | Gerenciar usuários, cadastro, login, JWT/OAuth2, recuperação de senha e permissões por perfil. |
| Pessoa 5 | **API Pública / Pokémon** | Consultar Pokémon, tipos, atributos, evoluções e integrar dados da [PokéAPI](https://pokeapi.co/). |

## Tecnologias

- **FastAPI:** endpoints HTTP e documentação interativa em `/docs`.
- **SQLAlchemy:** modelos, relacionamentos e acesso ao banco de dados.
- **SQLite:** banco local para desenvolvimento.
- **PostgreSQL:** banco recomendado para produção no Render.
- **Pydantic:** validação dos dados de entrada e saída.
- **JWT com OAuth2:** autenticação das rotas protegidas.
- **PokéAPI:** consulta externa de dados de Pokémon.

## Executar localmente

No PowerShell, dentro da pasta do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m fastapi dev app/main.py
```

Se a ativação do ambiente virtual for bloqueada:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Acesse:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Banco de dados e deploy no Render

Sim, você pode e deve manter os arquivos de banco local no `.gitignore`:

```gitignore
*.db
*.sqlite
*.sqlite3
```

O arquivo `pokedex.db` não deve ser enviado ao Git, pois é um artefato local e pode conter dados de desenvolvimento. Porém, ignorá-lo não cria persistência no Render. O filesystem padrão do Render é efêmero, então um SQLite gravado no diretório do projeto pode ser perdido em reinícios, novos deploys ou alterações da aplicação.

Para produção:

1. Crie um banco **Render Postgres**.
2. Configure no Web Service a variável `DATABASE_URL` com a URL interna do banco.
3. Configure também uma `SECRET_KEY` forte, com pelo menos 32 caracteres.
4. Use o comando de build `pip install -r requirements.txt`.
5. Use o comando de start:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O código escolhe a conexão pelo valor de `DATABASE_URL`. Sem essa variável, ele usa `sqlite:///./pokedex.db`, adequado apenas para desenvolvimento local. Para um SQLite persistente no Render, seria necessário configurar um Persistent Disk e apontar o banco para um caminho dentro desse disco; PostgreSQL continua sendo a opção recomendada para produção.

### Seed de usuários de demonstração

Para criar os usuários de demonstração manualmente, execute:

```powershell
python -m app.seed
```

A seed é idempotente: e-mails que já existem são ignorados. Para que a aplicação repovoe automaticamente o banco quando ele for recriado no Render, adicione esta variável de ambiente:

```env
SEED_DEFAULT_USERS=true
```

Usuários criados pela seed:

| Perfil | Nome | E-mail | Senha inicial |
|---|---|---|---|
| Treinador | Ash Ketchum | `ash@pokedex.example.com` | `Pokemon@123` |
| Treinador | Misty | `misty@pokedex.example.com` | `Pokemon@123` |
| Treinador | Brock | `brock@pokedex.example.com` | `Pokemon@123` |
| Treinador | May | `may@pokedex.example.com` | `Pokemon@123` |
| Treinador | Dawn | `dawn@pokedex.example.com` | `Pokemon@123` |
| Pesquisador | Professor Oak | `oak@pokedex.example.com` | `Pokemon@123` |
| Pesquisador | Professor Elm | `elm@pokedex.example.com` | `Pokemon@123` |
| Pesquisador | Professor Birch | `birch@pokedex.example.com` | `Pokemon@123` |
| Pesquisador | Professor Rowan | `rowan@pokedex.example.com` | `Pokemon@123` |
| Pesquisador | Professor Juniper | `juniper@pokedex.example.com` | `Pokemon@123` |
| Administrador | Cynthia | `cynthia@pokedex.example.com` | `Pokemon@123` |
| Administrador | Professor Kukui | `kukui@pokedex.example.com` | `Pokemon@123` |

Essas credenciais são apenas para demonstração. Em produção, use uma seed privada ou altere todas as senhas imediatamente. A seed não substitui um banco persistente: se o banco gratuito for apagado, ela apenas recria os usuários, não os demais dados da aplicação.

## Variáveis de ambiente

Exemplo para desenvolvimento em um arquivo `.env`:

```env
DATABASE_URL=sqlite:///./pokedex.db
SECRET_KEY=troque-por-uma-chave-secreta-com-mais-de-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=60
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
SEED_DEFAULT_USERS=false
```

Nunca publique `.env`, tokens, senhas ou chaves reais no repositório.

## Fluxo de autenticação

1. Crie uma conta com `POST /auth/register`.
2. Faça login com `POST /auth/login` usando formulário OAuth2.
3. Informe o e-mail no campo `username` e a senha no campo `password`.
4. Copie o `access_token` retornado.
5. No Swagger, clique em **Authorize** e informe o token.
6. A API valida o JWT e aplica a permissão de `TREINADOR`, `PESQUISADOR` ou `ADMINISTRADOR`.

Exemplo de cadastro:

```json
{
  "nome": "Jorge",
  "email": "jorge@exemplo.com",
  "senha": "minhaSenha123",
  "tipo_usuario": "TREINADOR"
}
```

## Endpoints principais

### Autenticação e usuários

| Método | Endpoint | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/auth/register` | Público | Cadastra um usuário. |
| `POST` | `/auth/login` | Público | Retorna um JWT. |
| `GET` | `/auth/users` | Administrador | Lista os usuários cadastrados. |
| `POST` | `/auth/password-recovery` | Público | Solicita recuperação de senha. |
| `POST` | `/auth/password-reset` | Público | Endpoint reservado para integração de redefinição. |

### Treinador

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/trainers/me/capturas` | Registra uma captura. |
| `GET` | `/trainers/me/capturas` | Lista a Pokédex pessoal. |
| `POST` | `/trainers/me/favoritos` | Marca uma captura como favorita. |
| `GET` | `/trainers/me/favoritos` | Lista os favoritos. |
| `GET` | `/trainers/me/pokedex/export` | Exporta um resumo da Pokédex pessoal. |

### Pesquisador e Pokémon

| Método | Endpoint | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/pokemons` | Autenticado | Busca espécies por nome ou tipo. |
| `GET` | `/pokemons/{pokemon_id}` | Autenticado | Consulta uma espécie. |
| `GET` | `/pokemons/{pokemon_id}/evolucoes` | Autenticado | Consulta a cadeia de evolução. |
| `POST` | `/pokemons` | Pesquisador/Admin | Cadastra uma espécie. |
| `POST` | `/pokemons/{pokemon_id}/evolucoes` | Pesquisador/Admin | Registra uma evolução. |
| `POST` | `/pokemons/compare` | Autenticado | Compara atributos de Pokémon. |
| `GET` | `/pokemons/public-api/{nome}` | Pesquisador/Admin | Consulta dados na PokéAPI sem gravar no banco. |
| `POST` | `/propostas` | Pesquisador | Envia uma proposta de alteração. |

### Administrador

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/propostas` | Lista propostas pendentes. |
| `POST` | `/propostas/{proposta_id}/review` | Aprova ou rejeita uma proposta. |
| `PUT` | `/pokemons/{pokemon_id}` | Edita um registro. |
| `DELETE` | `/pokemons/{pokemon_id}` | Remove um registro. |
| `GET` | `/reports/statistics` | Consulta estatísticas do sistema. |
| `GET` | `/audit-logs` | Consulta o histórico de auditoria. |

A lista completa de campos, respostas e códigos HTTP está disponível no Swagger em `/docs`.

## Estrutura do projeto

```text
app/
├── core/            # configurações, JWT e regras de permissão
├── models/          # tabelas e relacionamentos SQLAlchemy
├── schemas/         # validação de entrada e saída com Pydantic
├── routers/         # endpoints separados por domínio
├── database.py      # engine, sessões e conexão com o banco
└── main.py          # criação da aplicação e registro dos routers
```

Fluxo típico de uma requisição:

```text
Cliente -> Router -> Schema -> Regra de permissão -> Model/Banco -> JSON
```

## Próximos passos

- Usar Alembic para versionar migrações do banco.
- Criar testes automatizados para autenticação, permissões e endpoints.
- Finalizar a integração de recuperação e redefinição de senha.
