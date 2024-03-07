from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base

pokemon_type_association_table = Table(
    "pokemon_type_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("type_id", Integer, ForeignKey("type.id")),
)


class PokeType(Base):
    """PokeType is the pokemon type."""

    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Pokemon(Base):
    """Model definition for pokemo."""

    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    pre_evolve_id = Column(Integer, ForeignKey("pokemon.id"))
    types = relationship("PokeType", secondary=pokemon_type_association_table)
    pre_evolve = relationship("Pokemon", remote_side=[id])
    images: dict[str, str] = Column(JSONB)

    def __repr__(self):
        """
        Returns a string representation of the pokemon. This is useful for debugging purposes.

        @return A string representation of the pokemon in the form ` ` <Pokemon ( id = { id } name = { name }
        """
        return f"<Pokemon(id={self.id}, name={self.name})>"
