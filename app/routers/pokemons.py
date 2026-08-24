from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_user,
    require_administrador,
    require_pesquisador_ou_administrador,
)
from app.core.config import settings
from app.database import get_db
from app.models.auditoria import LogAuditoria
from app.models.pokemon import Evolucao, Pokemon, Tipo
from app.models.usuario import Pesquisador, Usuario
from app.schemas.pokemon import (
    CompararAtributosRequest,
    CompararAtributosResponse,
    EvolucaoCreate,
    EvolucaoRead,
    PokemonCreate,
    PokemonRead,
    PokemonUpdate,
    PublicApiPokemonResult,
)

router = APIRouter(prefix="/pokemons", tags=["Pokémon"])

POKEAPI_BASE_URL = settings.pokeapi_base_url.rstrip("/")


def _get_or_create_tipos(db: Session, nomes: List[str]) -> List[Tipo]:
    """Reutiliza tipos existentes e cria somente os que ainda não existem."""
    tipos = []
    for nome in nomes:
        tipo = db.query(Tipo).filter(Tipo.nome == nome.lower()).first()
        if not tipo:
            tipo = Tipo(nome=nome.lower())
            db.add(tipo)
            db.flush()
        tipos.append(tipo)
    return tipos


@router.get(
    "/public-api/{nome}",
    response_model=PublicApiPokemonResult,
    dependencies=[Depends(require_pesquisador_ou_administrador)],
)
def consultar_api_publica(nome: str):
    """
    Consulta a PokéAPI e adapta a resposta para o contrato desta aplicação.

    Nenhuma informação é gravada no banco; a rota serve de apoio ao cadastro.
    """
    try:
        resp = httpx.get(f"{POKEAPI_BASE_URL}/pokemon/{nome.lower()}", timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Falha ao consultar API pública externa")

    data = resp.json()
    # A PokéAPI envia os atributos em uma lista; o dicionário facilita buscar
    # cada valor pelo nome (attack, defense, speed e hp).
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    return PublicApiPokemonResult(
        nome=data["name"],
        id_externo=data["id"],
        tipos=[t["type"]["name"] for t in data["types"]],
        ataque=stats.get("attack", 0),
        defesa=stats.get("defense", 0),
        velocidade=stats.get("speed", 0),
        hp=stats.get("hp", 0),
        sprite_url=data.get("sprites", {}).get("front_default"),
    )


@router.post(
    "",
    response_model=PokemonRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_especie(
    payload: PokemonCreate,
    db: Session = Depends(get_db),
    current_user: Pesquisador = Depends(require_pesquisador_ou_administrador),
):
    """Cadastra uma espécie no banco (Pesquisador ou Administrador)."""
    if db.query(Pokemon).filter(Pokemon.numero_pokedex == payload.numero_pokedex).first():
        raise HTTPException(status_code=400, detail="Número de Pokedex já cadastrado")

    # Tipos são tratados separadamente porque a relação Pokemon-Tipo é N:N.
    dados = payload.model_dump(exclude={"tipos"})
    pokemon = Pokemon(**dados)
    pokemon.tipos = _get_or_create_tipos(db, payload.tipos)
    db.add(pokemon)
    db.commit()
    db.refresh(pokemon)

    # No diagrama, LogAuditoria só se associa a Administrador; quando quem
    # cadastra é um Pesquisador, não há log (ver README para essa decisão).
    from app.models.usuario import Administrador
    if isinstance(current_user, Administrador):
        db.add(LogAuditoria(
            administrador_id=current_user.id,
            acao="CADASTRAR_ESPECIE",
            entidade="Pokemon",
            entidade_id=pokemon.id,
        ))
        db.commit()
    return pokemon


@router.get("", response_model=List[PokemonRead])
def buscar_pokemons(
    nome: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Caso de uso Consultar/Buscar Pokemon (Treinador)."""
    query = db.query(Pokemon)
    if nome:
        query = query.filter(Pokemon.nome.ilike(f"%{nome}%"))
    if tipo:
        query = query.join(Pokemon.tipos).filter(Tipo.nome == tipo.lower())
    return query.all()


@router.get("/{pokemon_id}", response_model=PokemonRead)
def obter_pokemon(
    pokemon_id: int,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
    return pokemon


@router.post("/{pokemon_id}/evolucoes", response_model=EvolucaoRead, status_code=status.HTTP_201_CREATED)
def registrar_evolucao(
    pokemon_id: int,
    payload: EvolucaoCreate,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(require_pesquisador_ou_administrador),
):
    """Composição Pokemon 'compõe' Evolucao."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")

    evolucao = Evolucao(pokemon_origem_id=pokemon_id, **payload.model_dump())
    db.add(evolucao)
    db.commit()
    db.refresh(evolucao)
    return evolucao


@router.get("/{pokemon_id}/evolucoes", response_model=List[EvolucaoRead])
def visualizar_cadeia_de_evolucao(
    pokemon_id: int,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Caso de uso Visualizar Cadeia de Evolução (Treinador / Pesquisador)."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
    return pokemon.evolucoes


@router.post("/compare", response_model=CompararAtributosResponse)
def comparar_atributos(
    payload: CompararAtributosRequest,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Caso de uso Comparar Atributos (Treinador / Pesquisador), usando getAtributosCombate()."""
    pokemons = db.query(Pokemon).filter(Pokemon.id.in_(payload.pokemon_ids)).all()
    if len(pokemons) != len(payload.pokemon_ids):
        raise HTTPException(status_code=404, detail="Um ou mais Pokémon não encontrados")

    comparacao: dict[str, dict[str, int]] = {}
    for p in pokemons:
        for atributo, valor in p.get_atributos_combate().items():
            comparacao.setdefault(atributo, {})[p.nome] = valor

    return CompararAtributosResponse(pokemons=pokemons, comparacao=comparacao)


@router.put(
    "/{pokemon_id}",
    response_model=PokemonRead,
    dependencies=[Depends(require_administrador)],
)
def editar_registro(
    pokemon_id: int,
    payload: PokemonUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_administrador),
):
    """Caso de uso Editar / Remover Registro (Administrador) — edição."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")

    dados = payload.model_dump(exclude_unset=True, exclude={"tipos"})
    for campo, valor in dados.items():
        setattr(pokemon, campo, valor)
    if payload.tipos is not None:
        pokemon.tipos = _get_or_create_tipos(db, payload.tipos)

    db.commit()
    db.refresh(pokemon)

    db.add(LogAuditoria(
        administrador_id=current_user.id,
        acao="EDITAR_REGISTRO",
        entidade="Pokemon",
        entidade_id=pokemon.id,
    ))
    db.commit()
    return pokemon


@router.delete(
    "/{pokemon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_administrador)],
)
def remover_registro(
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_administrador),
):
    """Caso de uso Editar / Remover Registro (Administrador) — remoção."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")

    db.add(LogAuditoria(
        administrador_id=current_user.id,
        acao="REMOVER_REGISTRO",
        entidade="Pokemon",
        entidade_id=pokemon.id,
    ))
    db.delete(pokemon)
    db.commit()
