"""
Notificacao — não presente no diagrama de classe (vem do diagrama de
casos de uso, RECEBER NOTIFICAÇÃO DE EVOLUÇÃO). Mantida como extensão.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    treinador_id = Column(Integer, ForeignKey("treinadores.id"), nullable=False)
    captura_id = Column(Integer, ForeignKey("capturas.id"), nullable=True)
    mensagem = Column(String(255), nullable=False)
    lida = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    treinador = relationship("Treinador", back_populates="notificacoes")
    captura = relationship("Captura", back_populates="notificacoes")
