"""Cria usuarios de demonstracao sem duplicar registros existentes."""

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import Administrador, Pesquisador, Treinador, Usuario

SENHA_PADRAO = "Pokemon@123"

USUARIOS_SEED = (
    ("Ash Ketchum", "ash@pokedex.local", Treinador),
    ("Misty", "misty@pokedex.local", Treinador),
    ("Brock", "brock@pokedex.local", Treinador),
    ("May", "may@pokedex.local", Treinador),
    ("Dawn", "dawn@pokedex.local", Treinador),
    ("Professor Oak", "oak@pokedex.local", Pesquisador),
    ("Professor Elm", "elm@pokedex.local", Pesquisador),
    ("Professor Birch", "birch@pokedex.local", Pesquisador),
    ("Professor Rowan", "rowan@pokedex.local", Pesquisador),
    ("Professor Juniper", "juniper@pokedex.local", Pesquisador),
    ("Cynthia", "cynthia@pokedex.local", Administrador),
    ("Professor Kukui", "kukui@pokedex.local", Administrador),
)


def seed_users(db: Session) -> int:
    """Insere os usuarios de demonstracao e retorna quantos foram criados."""
    criados = 0
    senha_hash = get_password_hash(SENHA_PADRAO)

    for nome, email, classe_usuario in USUARIOS_SEED:
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            continue

        db.add(
            classe_usuario(
                nome=nome,
                email=email,
                senha_hash=senha_hash,
                ativo=True,
            )
        )
        criados += 1

    if criados:
        db.commit()
    return criados


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        criados = seed_users(db)
    print(f"Seed concluida: {criados} usuario(s) criado(s).")


if __name__ == "__main__":
    main()
