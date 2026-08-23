"""LogAuditoria — registrado pelo Administrador."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    acao = Column(String(100), nullable=False)
    data_hora = Column(DateTime(timezone=True), server_default=func.now())

    administrador_id = Column(Integer, ForeignKey("administradores.id"), nullable=False)
    administrador = relationship("Administrador", back_populates="logs")

    # Campos extras (não no diagrama) para facilitar filtragem por entidade
    entidade = Column(String(50), nullable=True)
    entidade_id = Column(Integer, nullable=True)
