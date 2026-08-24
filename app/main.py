from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.core.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auditoria, auth, capturas, notificacoes, pokemons, propostas, reports
from app.seed import seed_users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Cria as tabelas que ainda não existirem quando a API iniciar.
    # Em produção, o ideal é aplicar migrações com Alembic.
    Base.metadata.create_all(bind=engine)
    if settings.seed_default_users:
        with SessionLocal() as db:
            seed_users(db)
    yield

app = FastAPI(
    title=settings.app_name,
    description=(
        "API baseada no diagrama de classes: Usuario (abstrato) "
        "especializado em Treinador, Pesquisador e Administrador, "
        "além de Pokemon, Tipo, Evolucao, Captura, Proposta e LogAuditoria."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

# Cada router concentra endpoints de um domínio. Incluí-los aqui faz as
# rotas ficarem disponíveis na documentação em /docs.
app.include_router(auth.router)
app.include_router(pokemons.router)
app.include_router(capturas.router)
app.include_router(propostas.router)
app.include_router(reports.router)
app.include_router(auditoria.router)
app.include_router(notificacoes.router)


@app.get("/health", tags=["Saúde da API"])
def health_check():
    """Endpoint simples para verificar se a aplicação está no ar."""
    return {"status": "ok", "service": settings.app_name}


@app.get("/", tags=["Início"])
def root():
    """Apresenta uma resposta mínima ao acessar a raiz da API."""
    return {"status": "ok", "system": settings.app_name}
