from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---- Registrar Captura ----
class CapturaCreate(BaseModel):
    pokemon_id: int
    local: Optional[str] = None
    nivel: int = 1
    is_shiny: bool = False


class CapturaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    treinador_id: int
    pokemon_id: int
    data_captura: date
    local: Optional[str] = None
    nivel: int
    is_shiny: bool


# ---- Marcar Favorito (extensão) ----
class FavoritoCreate(BaseModel):
    captura_id: int


class FavoritoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    treinador_id: int
    captura_id: int
    criado_em: datetime


# ---- Exportar Pokedex Pessoal ----
class PokedexExportEntry(BaseModel):
    pokemon_nome: str
    numero_pokedex: int
    is_shiny: bool
    nivel: int
    local: Optional[str] = None
    data_captura: date


class PokedexExport(BaseModel):
    treinador_nome: str
    total_capturado: int
    total_shiny: int
    entradas: List[PokedexExportEntry]
