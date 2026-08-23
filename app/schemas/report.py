from typing import Dict

from pydantic import BaseModel


class Relatorio(BaseModel):
    """+gerarRelatorio(): Relatorio (Administrador / Pesquisador)."""
    total_pokemons: int
    total_capturas: int
    total_capturas_shiny: int
    pokemons_por_tipo: Dict[str, int]
    capturas_por_treinador: Dict[str, int]
    propostas_pendentes: int
