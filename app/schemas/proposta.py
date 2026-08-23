from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---- Propor Alteracao (Pesquisador) ----
class PropostaCreate(BaseModel):
    pokemon_id: int
    dados_depois: str  # texto livre descrevendo a alteração proposta


class PropostaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    pokemon_id: int
    pesquisador_id: int
    dados_antes: Optional[str] = None
    dados_depois: str
    administrador_id: Optional[int] = None
    revisado_em: Optional[datetime] = None
    criado_em: datetime


# ---- Aprovar/Recusar Proposta (Administrador) ----
class PropostaReview(BaseModel):
    aprovar: bool
