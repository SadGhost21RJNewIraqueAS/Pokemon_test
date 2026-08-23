from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_administrador, require_pesquisador
from app.database import get_db
from app.models.auditoria import LogAuditoria
from app.models.pokemon import Pokemon
from app.models.proposta import Proposta
from app.models.usuario import Administrador, Pesquisador
from app.schemas.proposta import PropostaCreate, PropostaRead, PropostaReview

router = APIRouter(prefix="/propostas", tags=["Propostas de Alteração"])


@router.post("", response_model=PropostaRead, status_code=status.HTTP_201_CREATED)
def propor_alteracao(
    payload: PropostaCreate,
    db: Session = Depends(get_db),
    current_user: Pesquisador = Depends(require_pesquisador),
):
    """+proporAlteracao(): Proposta (Pesquisador)."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == payload.pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")

    # dadosAntes é capturado automaticamente a partir do estado atual
    dados_antes = (
        f"nome={pokemon.nome}, descricao={pokemon.descricao}, "
        f"ataque={pokemon.ataque}, defesa={pokemon.defesa}, "
        f"velocidade={pokemon.velocidade}, hp={pokemon.hp}"
    )

    proposta = Proposta(
        pokemon_id=payload.pokemon_id,
        pesquisador_id=current_user.id,
        dados_antes=dados_antes,
        dados_depois=payload.dados_depois,
    )
    db.add(proposta)
    db.commit()
    db.refresh(proposta)
    return proposta


@router.get("", response_model=List[PropostaRead], dependencies=[Depends(require_administrador)])
def listar_propostas_pendentes(db: Session = Depends(get_db)):
    return db.query(Proposta).filter(Proposta.status == "pendente").all()


@router.post("/{proposta_id}/review", response_model=PropostaRead)
def aprovar_ou_recusar_proposta(
    proposta_id: int,
    payload: PropostaReview,
    db: Session = Depends(get_db),
    current_user: Administrador = Depends(require_administrador),
):
    """+aprovarProposta(): void (Administrador)."""
    proposta = db.query(Proposta).filter(Proposta.id == proposta_id).first()
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    if proposta.status != "pendente":
        raise HTTPException(status_code=400, detail="Proposta já foi revisada")

    proposta.status = "aprovada" if payload.aprovar else "recusada"
    proposta.administrador_id = current_user.id
    proposta.revisado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposta)

    db.add(LogAuditoria(
        administrador_id=current_user.id,
        acao="APROVAR_PROPOSTA" if payload.aprovar else "RECUSAR_PROPOSTA",
        entidade="Proposta",
        entidade_id=proposta.id,
    ))
    db.commit()
    return proposta
