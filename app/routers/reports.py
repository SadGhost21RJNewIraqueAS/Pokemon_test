from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_pesquisador_ou_administrador
from app.database import get_db
from app.models.captura import Captura
from app.models.pokemon import Pokemon
from app.models.proposta import Proposta
from app.schemas.report import Relatorio

router = APIRouter(prefix="/reports", tags=["Relatórios"])


@router.get(
    "/statistics",
    response_model=Relatorio,
    dependencies=[Depends(require_pesquisador_ou_administrador)],
)
def gerar_relatorio(db: Session = Depends(get_db)):
    """+gerarRelatorio(): Relatorio (Pesquisador / Administrador)."""
    pokemons = db.query(Pokemon).all()
    capturas = db.query(Captura).all()

    pokemons_por_tipo = Counter()
    for p in pokemons:
        for t in p.tipos:
            pokemons_por_tipo[t.nome] += 1

    capturas_por_treinador = Counter(c.treinador.nome for c in capturas)
    propostas_pendentes = db.query(Proposta).filter(Proposta.status == "pendente").count()

    return Relatorio(
        total_pokemons=len(pokemons),
        total_capturas=len(capturas),
        total_capturas_shiny=sum(1 for c in capturas if c.is_shiny),
        pokemons_por_tipo=dict(pokemons_por_tipo),
        capturas_por_treinador=dict(capturas_por_treinador),
        propostas_pendentes=propostas_pendentes,
    )
