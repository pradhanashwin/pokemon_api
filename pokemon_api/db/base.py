from sqlalchemy.orm import DeclarativeBase

from pokemon_api.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
