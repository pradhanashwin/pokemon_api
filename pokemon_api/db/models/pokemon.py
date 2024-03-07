from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base

pokemon_type_association_table = Table(
    "pokemon_type_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("type_id", Integer, ForeignKey("type.id")),
)

pokemon_move_association = Table(
    "pokemon_move_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("move_id", Integer, ForeignKey("move.id")),
)


class PokeMove(Base):
    """PokeMove is the pokemon move."""

    __tablename__ = "move"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    pokemons = relationship(
        "Pokemon",
        secondary=pokemon_move_association,
        back_populates="moves",
    )


class PokeType(Base):
    """PokeType is the pokemon type."""

    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    pokemons = relationship(
        "Pokemon",
        secondary=pokemon_type_association_table,
        back_populates="types",
    )


class PokeGeneration(Base):
    """PokeGeneration is the pokemon Generation."""

    __tablename__ = "generation"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    region = Column(String(255), nullable=False)
    pokemons = relationship("Pokemon", back_populates="generation")


class Pokemon(Base):
    """Model definition for pokemo."""

    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    types = relationship(
        "PokeType",
        secondary=pokemon_type_association_table,
        back_populates="pokemons",
    )
    images = Column(JSONB)
    generation_id = Column(Integer, ForeignKey("generation.id"))
    generation = relationship("PokeGeneration", back_populates="pokemons")
    moves = relationship(
        "PokeMove",
        secondary=pokemon_move_association,
        back_populates="pokemons",
    )
    is_legendary = Column(Boolean, default=False)

    def __repr__(self):
        """
        Returns a string representation of the pokemon. This is useful for debugging purposes.

        @return A string representation of the pokemon in the form ` ` <Pokemon ( id = { id } name = { name }
        """
        return f"<Pokemon(id={self.id}, name={self.name})>"
