from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---- Visualizar Auditoria (Administrador) ----
class LogAuditoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    administrador_id: int
    acao: str
    data_hora: datetime
    entidade: Optional[str] = None
    entidade_id: Optional[int] = None
