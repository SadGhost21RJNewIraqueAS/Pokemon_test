from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_treinador
from app.database import get_db
from app.models.captura import Captura, Favorito
from app.models.notificacao import Notificacao
from app.models.pokemon import Pokemon
from app.models.usuario import Treinador
from app.schemas.captura import (
    CapturaCreate,
    CapturaRead,
    FavoritoCreate,
    FavoritoRead,
    PokedexExport,
    PokedexExportEntry,
)

router = APIRouter(prefix="/trainers/me", tags=["Treinador"])


@router.post("/capturas", response_model=CapturaRead, status_code=status.HTTP_201_CREATED)
def registrar_captura(
    payload: CapturaCreate,
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    """Caso de uso Registrar Captura (Treinador)."""
    pokemon = db.query(Pokemon).filter(Pokemon.id == payload.pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")

    captura = Captura(**payload.model_dump(), treinador_id=current_user.id)
    db.add(captura)
    db.commit()
    db.refresh(captura)

    # Se o Pokémon possui evoluções cadastradas, notifica o treinador
    if pokemon.evolucoes:
        db.add(Notificacao(
            treinador_id=current_user.id,
            captura_id=captura.id,
            mensagem=f"{pokemon.nome} pode evoluir! Confira os requisitos.",
        ))
        db.commit()

    return captura


@router.get("/capturas", response_model=List[CapturaRead])
def listar_pokedex_pessoal(
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    """-List<Captura> pokedexPessoal."""
    return db.query(Captura).filter(Captura.treinador_id == current_user.id).all()


@router.post("/favoritos", response_model=FavoritoRead, status_code=status.HTTP_201_CREATED)
def marcar_favorito(
    payload: FavoritoCreate,
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    captura = (
        db.query(Captura)
        .filter(Captura.id == payload.captura_id, Captura.treinador_id == current_user.id)
        .first()
    )
    if not captura:
        raise HTTPException(status_code=404, detail="Captura não encontrada")

    existente = (
        db.query(Favorito)
        .filter(Favorito.captura_id == payload.captura_id, Favorito.treinador_id == current_user.id)
        .first()
    )
    if existente:
        return existente

    favorito = Favorito(treinador_id=current_user.id, captura_id=payload.captura_id)
    db.add(favorito)
    db.commit()
    db.refresh(favorito)
    return favorito


@router.get("/favoritos", response_model=List[FavoritoRead])
def listar_favoritos(
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    return db.query(Favorito).filter(Favorito.treinador_id == current_user.id).all()


@router.get("/pokedex/export", response_model=PokedexExport)
def exportar_pokedex(
    db: Session = Depends(get_db),
    current_user: Treinador = Depends(require_treinador),
):
    """+exportarPokedex(): Arquivo."""
    capturas = db.query(Captura).filter(Captura.treinador_id == current_user.id).all()

    entradas = [
        PokedexExportEntry(
            pokemon_nome=c.pokemon.nome,
            numero_pokedex=c.pokemon.numero_pokedex,
            is_shiny=c.is_shiny,
            nivel=c.nivel,
            local=c.local,
            data_captura=c.data_captura,
        )
        for c in capturas
    ]

    return PokedexExport(
        treinador_nome=current_user.nome,
        total_capturado=len(entradas),
        total_shiny=sum(1 for e in entradas if e.is_shiny),
        entradas=entradas,
    )
