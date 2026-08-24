"""Cria usuarios de demonstracao sem duplicar registros existentes."""

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import Administrador, Pesquisador, Treinador, Usuario

SENHA_PADRAO = "Pokemon@123"
DOMINIO_LEGADO = "pokedex.local"

USUARIOS_SEED = (
    ("Ash Ketchum", "ash@pokedex.example.com", Treinador),
    ("Misty", "misty@pokedex.example.com", Treinador),
    ("Brock", "brock@pokedex.example.com", Treinador),
    ("May", "may@pokedex.example.com", Treinador),
    ("Dawn", "dawn@pokedex.example.com", Treinador),
    ("Professor Oak", "oak@pokedex.example.com", Pesquisador),
    ("Professor Elm", "elm@pokedex.example.com", Pesquisador),
    ("Professor Birch", "birch@pokedex.example.com", Pesquisador),
    ("Professor Rowan", "rowan@pokedex.example.com", Pesquisador),
    ("Professor Juniper", "juniper@pokedex.example.com", Pesquisador),
    ("Cynthia", "cynthia@pokedex.example.com", Administrador),
    ("Professor Kukui", "kukui@pokedex.example.com", Administrador),
)


def seed_users(db: Session) -> int:
    """Insere os usuarios de demonstracao e retorna quantos foram criados."""
    criados = 0
    senha_hash = get_password_hash(SENHA_PADRAO)

    for nome, email, classe_usuario in USUARIOS_SEED:
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente is None:
            email_legado = email.replace("pokedex.example.com", DOMINIO_LEGADO)
            existente = db.query(Usuario).filter(Usuario.email == email_legado).first()
            if existente:
                existente.email = email
                criados += 1
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
