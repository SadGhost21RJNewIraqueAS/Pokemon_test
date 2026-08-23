from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.core.config import settings
from app.database import Base, engine
from app.routers import auditoria, auth, capturas, notificacoes, pokemons, propostas, reports


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.app_name,
    description=(
        "API baseada no diagrama de classe: Usuario (abstrato) "
        "especializado em Treinador, Pesquisador e Administrador, "
        "além de Pokemon, Tipo, Evolucao, Captura, Proposta e LogAuditoria."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(pokemons.router)
app.include_router(capturas.router)
app.include_router(propostas.router)
app.include_router(reports.router)
app.include_router(auditoria.router)
app.include_router(notificacoes.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.app_name}


@app.get("/", tags=["Root"])
def root():
    return {"status": "ok", "system": settings.app_name}
