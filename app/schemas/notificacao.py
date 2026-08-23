from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    treinador_id: int
    captura_id: Optional[int] = None
    mensagem: str
    lida: bool
    criado_em: datetime
