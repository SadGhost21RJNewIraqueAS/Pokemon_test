"""
Usuario (abstrato) e suas especializações: Treinador, Pesquisador,
Administrador — mapeados com herança de tabelas (joined-table
inheritance), refletindo a generalização/especialização do diagrama.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    """Classe abstrata do diagrama. Não é instanciada diretamente."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Discriminador da herança (equivalente ao "tipo" de cada subclasse)
    tipo_usuario = Column(String(20), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "usuario",
        "polymorphic_on": tipo_usuario,
    }

    def autenticar(self, senha: str) -> bool:
        """+autenticar(senha): boolean — não depende do banco, fica no model."""
        from app.core.security import verify_password
        return verify_password(senha, self.senha_hash)

    def recuperar_senha(self) -> None:
        """+recuperarSenha(): void — delega ao Sistema Externo 'API de Autenticação'."""
        # Implementação real (envio de e-mail/token) fica no router de auth,
        # que é quem tem acesso a serviços externos e ao banco.
        pass


class Treinador(Usuario):
    """
    -List<Captura> pokedexPessoal
    +registrarCaptura(), +compararAtributos(), +exportarPokedex()
    Os três métodos dependem do banco (e, no caso de compararAtributos,
    de outros Pokémon), então viram endpoints em routers/capturas.py e
    routers/pokemons.py — a classe expõe apenas o relacionamento de dados.
    """
    __tablename__ = "treinadores"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "treinador"}

    capturas = relationship(
        "Captura", back_populates="treinador", cascade="all, delete-orphan"
    )  # pokedexPessoal
    favoritos = relationship(
        "Favorito", back_populates="treinador", cascade="all, delete-orphan"
    )
    notificacoes = relationship(
        "Notificacao", back_populates="treinador", cascade="all, delete-orphan"
    )


class Pesquisador(Usuario):
    """
    +cadastrarEspecie(): void
    +proporAlteracao(): Proposta
    Ambos dependem do banco -> routers/pokemons.py e routers/propostas.py.
    """
    __tablename__ = "pesquisadores"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "pesquisador"}

    propostas = relationship(
        "Proposta",
        back_populates="pesquisador",
        foreign_keys="Proposta.pesquisador_id",
    )


class Administrador(Usuario):
    """
    +aprovarProposta(): void
    +gerarRelatorio(): Relatorio
    +visualizarAuditoria(): List<LogAuditoria>
    Todos dependem do banco -> routers/propostas.py, reports.py, auditoria.py.
    """
    __tablename__ = "administradores"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "administrador"}

    logs = relationship("LogAuditoria", back_populates="administrador")
