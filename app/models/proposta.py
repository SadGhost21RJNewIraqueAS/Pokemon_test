"""Proposta de alteração — dadosAntes/dadosDepois como texto, conforme o diagrama."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Proposta(Base):
    __tablename__ = "propostas"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), default="pendente")  # pendente | aprovada | recusada
    dados_antes = Column(String(2000), nullable=True)
    dados_depois = Column(String(2000), nullable=False)

    pokemon_id = Column(Integer, ForeignKey("pokemons.id"), nullable=False)
    pokemon = relationship("Pokemon")

    pesquisador_id = Column(Integer, ForeignKey("pesquisadores.id"), nullable=False)
    pesquisador = relationship("Pesquisador", back_populates="propostas")

    # Não está no diagrama, mas é necessário para saber quem revisou
    # (equivalente a registrar o Administrador que executou aprovarProposta()).
    administrador_id = Column(Integer, ForeignKey("administradores.id"), nullable=True)
    administrador = relationship("Administrador")
    revisado_em = Column(DateTime(timezone=True), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
