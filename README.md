# Sistema Pokedex Digital — API FastAPI

Implementação baseada no **diagrama de classe** fornecido (Usuario abstrato
especializado em Treinador/Pesquisador/Administrador, Pokemon, Tipo,
Evolucao, Captura, Proposta, LogAuditoria).

## Instalação

```bash
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

As configurações ficam no arquivo `.env`. Em produção, defina uma
`SECRET_KEY` aleatória com pelo menos 32 caracteres e configure
`DATABASE_URL` para o banco desejado.

Documentação interativa: `http://localhost:8000/docs`

## Como o diagrama de classe virou código

| Elemento UML | Onde vira código |
|---|---|
| Classe (ex: `Pokemon`) | Classe SQLAlchemy em `app/models/` — representa a tabela |
| Atributos da classe | Colunas SQLAlchemy no mesmo arquivo |
| Associação/agregação (ex: Treinador 1—0..* Captura) | `ForeignKey` + `relationship()` nos dois lados |
| Composição (Pokemon 1—0..* Evolucao) | `relationship(..., cascade="all, delete-orphan")` — a Evolucao não sobrevive sem o Pokemon |
| Generalização (Usuario → Treinador/Pesquisador/Administrador) | **Herança de tabelas** (joined-table inheritance): tabela `usuarios` + uma tabela por subclasse, unidas por FK no `id`, com `polymorphic_on`/`polymorphic_identity` |
| Método sem dependência de banco (ex: `getAtributosCombate()`, `verificarRequisitos()`, `autenticar()`) | Vira um método de verdade dentro da própria classe do model |
| Método que depende do banco/outros usuários (ex: `registrarCaptura()`, `gerarRelatorio()`, `aprovarProposta()`) | Vira um **endpoint** no router correspondente — a classe não pode "ver" o banco sozinha, então essa lógica sobe uma camada |
| Multiplicidade (`0..*`, `1..*`) | Validada via schemas Pydantic (`Field(min_length=...)`) e regras no router, já que o SQLAlchemy não impõe isso sozinho |

`main.py` não contém nenhuma classe do diagrama — ele só monta o `FastAPI()`
e inclui os routers.

## Estrutura

```
app/
  core/
    security.py      # hashing de senha, JWT (delegado à API de Autenticação externa)
    deps.py           # autorização via isinstance(), reproduzindo o polimorfismo do diagrama
  models/
    usuario.py        # Usuario (abstrato) + Treinador, Pesquisador, Administrador
    pokemon.py         # Pokemon, Tipo (N:N), Evolucao (composição)
    captura.py         # Captura, Favorito (extensão)
    proposta.py        # Proposta
    auditoria.py       # LogAuditoria
    notificacao.py     # Notificacao (extensão)
  schemas/             # contratos Pydantic, um arquivo por domínio
  routers/
    auth.py            # Autenticar Usuario, Recuperar Senha
    pokemons.py        # Cadastrar Especie, Buscar, Comparar Atributos, Evolução, Editar/Remover
    capturas.py         # Registrar Captura, Favoritos, Exportar Pokedex
    propostas.py         # Propor Alteração, Aprovar/Recusar
    reports.py          # Gerar Relatório Estatístico
    auditoria.py         # Visualizar Histórico de Auditoria
    notificacoes.py       # Receber Notificação de Evolução
  database.py
  main.py
```

## Ator → Método UML → Endpoint

### Treinador (`Usuario` → herança)
| Método/atributo do diagrama | Endpoint |
|---|---|
| `pokedexPessoal` | `GET /trainers/me/capturas` |
| `registrarCaptura()` | `POST /trainers/me/capturas` |
| `compararAtributos()` | `POST /pokemons/compare` |
| `exportarPokedex()` | `GET /trainers/me/pokedex/export` |

### Pesquisador
| Método | Endpoint |
|---|---|
| `cadastrarEspecie()` | `POST /pokemons` |
| `proporAlteracao()` | `POST /propostas` |

### Administrador
| Método | Endpoint |
|---|---|
| `aprovarProposta()` | `POST /propostas/{id}/review` |
| `gerarRelatorio()` | `GET /reports/statistics` |
| `visualizarAuditoria()` | `GET /audit-logs` |

### Métodos "livres de banco" (ficam na própria classe)
- `Usuario.autenticar(senha)` — usado internamente por `POST /auth/login`
- `Pokemon.get_atributos_combate()` — usado por `POST /pokemons/compare`
- `Evolucao.verificar_requisitos(captura)` — disponível para uso futuro em regras de evolução automática

## Decisões e inferências (o que não estava 100% explícito no diagrama)

1. **`Evolucao.pokemon_destino_id`**: o diagrama define `condicao` e
   `verificarRequisitos()`, mas não mostra para qual Pokémon a evolução
   leva. Adicionei esse campo (opcional) porque sem ele a funcionalidade
   não faz sentido na prática — ajuste se seu modelo real representa isso
   de outro jeito (ex: nome do destino como string).
2. **`Proposta.administrador_id`**: o diagrama só mostra
   `Administrador 1—0..* LogAuditoria`, sem ligação direta com `Proposta`.
   Adicionei essa FK para saber quem aprovou/recusou cada proposta.
3. **`Proposta.dados_antes` / `dados_depois`** são strings (texto livre),
   como no diagrama — por isso a aprovação **não aplica automaticamente**
   a mudança no Pokémon; ela fica registrada como histórico/auditoria, e
   qualquer alteração real de dados usa o endpoint de edição do
   Administrador (`PUT /pokemons/{id}`).
4. **`Favorito` e `Notificacao`** não estão no diagrama de classe — vieram
   do diagrama de casos de uso (Marcar Favorito, Receber Notificação de
   Evolução) e foram mantidos como extensões, claramente comentadas no
   código. Remova-os se quiser ficar 100% restrito ao diagrama de classe.
5. **`LogAuditoria`** só é gerado por ações do `Administrador` (edição,
   remoção, aprovação/recusa de propostas), pois é assim que o diagrama
   liga essas duas classes.

## Observações técnicas

- Banco SQLite para simplicidade (`app/database.py`); troque a URL para
  PostgreSQL/MySQL em produção.
- O hash de senhas usa Argon2 por meio de `pwdlib`; JWT usa `PyJWT`.
- O schema é criado no startup para facilitar o desenvolvimento local.
  Para produção, use migrações versionadas com Alembic antes de remover
  essa criação automática.
