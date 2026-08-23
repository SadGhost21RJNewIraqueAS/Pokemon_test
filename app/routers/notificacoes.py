from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_treinador
from app.database import get_db
from app.models.notificacao import Notificacao
from app.models.usuario import Treinador
from app.schemas.notificacao import NotificacaoRead

router = APIRouter(prefix="/trainers/me/notificacoes", tags=["Notificações"])


@router.get("", response_model=List[NotificacaoRead])
def listar_notificacoes(
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    """Extensão do diagrama de casos de uso: Receber Notificação de Evolução."""
    return (
        db.query(Notificacao)
        .filter(Notificacao.treinador_id == current_user.id)
        .order_by(Notificacao.criado_em.desc())
        .all()
    )


@router.post("/{notificacao_id}/lida", response_model=NotificacaoRead)
def marcar_notificacao_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    notificacao = (
        db.query(Notificacao)
        .filter(Notificacao.id == notificacao_id, Notificacao.treinador_id == current_user.id)
        .first()
    )
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")

    notificacao.lida = True
    db.commit()
    db.refresh(notificacao)
    return notificacao
