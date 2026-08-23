from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_administrador
from app.database import get_db
from app.models.auditoria import LogAuditoria
from app.schemas.auditoria import LogAuditoriaRead

router = APIRouter(prefix="/audit-logs", tags=["Auditoria"])


@router.get("", response_model=List[LogAuditoriaRead], dependencies=[Depends(require_administrador)])
def visualizar_auditoria(
    entidade: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    """+visualizarAuditoria(): List<LogAuditoria> (Administrador)."""
    query = db.query(LogAuditoria)
    if entidade:
        query = query.filter(LogAuditoria.entidade == entidade)
    return query.order_by(LogAuditoria.data_hora.desc()).limit(limit).all()
