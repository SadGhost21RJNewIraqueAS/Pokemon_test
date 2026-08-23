"""Pokemon, Tipo (N:N) e Evolucao (composição), conforme o diagrama."""
import re

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from app.database import Base

# Associação N:N "possui" entre Pokemon e Tipo
pokemon_tipo = Table(
    "pokemon_tipo",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemons.id"), primary_key=True),
    Column("tipo_id", Integer, ForeignKey("tipos.id"), primary_key=True),
)


class Tipo(Base):
    __tablename__ = "tipos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)

    pokemons = relationship("Pokemon", secondary=pokemon_tipo, back_populates="tipos")


class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True, nullable=False)
    numero_pokedex = Column(Integer, unique=True, index=True, nullable=False)
    descricao = Column(String(1000), nullable=True)
    ataque = Column(Integer, nullable=False)
    defesa = Column(Integer, nullable=False)
    velocidade = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    imagem = Column(String(255), nullable=True)

    tipos = relationship("Tipo", secondary=pokemon_tipo, back_populates="pokemons")  # possui
    evolucoes = relationship(
        "Evolucao",
        back_populates="pokemon_origem",
        foreign_keys="Evolucao.pokemon_origem_id",
        cascade="all, delete-orphan",  # compõe: ciclo de vida ligado ao Pokemon
    )
    capturas = relationship("Captura", back_populates="pokemon")

    def get_atributos_combate(self) -> dict:
        """+getAtributosCombate(): Map — não depende do banco, fica no model."""
        return {
            "ataque": self.ataque,
            "defesa": self.defesa,
            "velocidade": self.velocidade,
            "hp": self.hp,
        }


class Evolucao(Base):
    """
    Relação de composição 'compõe' com Pokemon: uma Evolucao não existe
    sem o Pokemon de origem (por isso o cascade delete-orphan acima).

    Nota: o diagrama não define para qual Pokémon a evolução leva.
    Adicionei `pokemon_destino_id` como campo inferido, necessário para
    a funcionalidade fazer sentido — ajuste/remova se seu modelo real
    representa isso de outra forma (ex.: nome do destino como string).
    """
    __tablename__ = "evolucoes"

    id = Column(Integer, primary_key=True, index=True)
    condicao = Column(String(255), nullable=False)  # ex: "nivel 16", "pedra_fogo"

    pokemon_origem_id = Column(Integer, ForeignKey("pokemons.id"), nullable=False)
    pokemon_origem = relationship(
        "Pokemon", back_populates="evolucoes", foreign_keys=[pokemon_origem_id]
    )

    pokemon_destino_id = Column(Integer, ForeignKey("pokemons.id"), nullable=True)
    pokemon_destino = relationship("Pokemon", foreign_keys=[pokemon_destino_id])

    def verificar_requisitos(self, captura: "Captura") -> bool:
        """
        +verificarRequisitos(): boolean — não depende do banco, fica no model.
        Regra simplificada: extrai um número da condição e compara com o
        nível da captura (ex.: condicao="nivel 16" -> captura.nivel >= 16).
        """
        match = re.search(r"\d+", self.condicao)
        if match:
            nivel_minimo = int(match.group())
            return captura.nivel >= nivel_minimo
        return False
