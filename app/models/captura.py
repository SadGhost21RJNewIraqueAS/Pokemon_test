"""Captura (associação Treinador-Pokemon) e Favorito (extensão)."""
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Captura(Base):
    __tablename__ = "capturas"

    id = Column(Integer, primary_key=True, index=True)
    data_captura = Column(Date, server_default=func.current_date())
    local = Column(String(120), nullable=True)
    nivel = Column(Integer, default=1)
    is_shiny = Column(Boolean, default=False)

    treinador_id = Column(Integer, ForeignKey("treinadores.id"), nullable=False)
    pokemon_id = Column(Integer, ForeignKey("pokemons.id"), nullable=False)

    treinador = relationship("Treinador", back_populates="capturas")
    pokemon = relationship("Pokemon", back_populates="capturas")
    favoritos = relationship(
        "Favorito", back_populates="captura", cascade="all, delete-orphan"
    )
    notificacoes = relationship("Notificacao", back_populates="captura")


class Favorito(Base):
    """
    Não presente no diagrama de classe (vem do diagrama de casos de uso,
    caso de uso MARCAR FAVORITO). Mantido como extensão.
    """
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    treinador_id = Column(Integer, ForeignKey("treinadores.id"), nullable=False)
    captura_id = Column(Integer, ForeignKey("capturas.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    treinador = relationship("Treinador", back_populates="favoritos")
    captura = relationship("Captura", back_populates="favoritos")
