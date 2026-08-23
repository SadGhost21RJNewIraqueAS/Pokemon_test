from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TipoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


# ---- Cadastrar Especie (o Pesquisador informa os nomes dos tipos; o
# router resolve/cria as entidades Tipo correspondentes) ----
class PokemonCreate(BaseModel):
    nome: str
    numero_pokedex: int
    descricao: Optional[str] = None
    ataque: int
    defesa: int
    velocidade: int
    hp: int
    imagem: Optional[str] = None
    tipos: List[str] = Field(min_length=1)


class PokemonUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ataque: Optional[int] = None
    defesa: Optional[int] = None
    velocidade: Optional[int] = None
    hp: Optional[int] = None
    imagem: Optional[str] = None
    tipos: Optional[List[str]] = None


class PokemonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    numero_pokedex: int
    descricao: Optional[str] = None
    ataque: int
    defesa: int
    velocidade: int
    hp: int
    imagem: Optional[str] = None
    tipos: List[TipoRead] = []


# ---- Evolucao ----
class EvolucaoCreate(BaseModel):
    condicao: str
    pokemon_destino_id: Optional[int] = None


class EvolucaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    condicao: str
    pokemon_origem_id: int
    pokemon_destino_id: Optional[int] = None


# ---- Comparar Atributos ----
class CompararAtributosRequest(BaseModel):
    pokemon_ids: List[int] = Field(min_length=2, max_length=6)


class CompararAtributosResponse(BaseModel):
    pokemons: List[PokemonRead]
    comparacao: Dict[str, Dict[str, int]]  # {"ataque": {"Charizard": 84, ...}, ...}


# ---- Consultar API Pública (<<include>>) ----
class PublicApiPokemonResult(BaseModel):
    nome: str
    id_externo: int
    tipos: List[str]
    ataque: int
    defesa: int
    velocidade: int
    hp: int
    sprite_url: Optional[str] = None
