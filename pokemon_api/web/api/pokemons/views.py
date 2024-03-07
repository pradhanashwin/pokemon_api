from fastapi import APIRouter, Request
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from pokemon_api.db.models.pokemon import Pokemon, PokeType

router = APIRouter()


@router.get("/pokemon/{pokemon_id}")
async def get_pokemon(pokemon_id: int, request: Request):
    """
    Get a pokemon by id.

    @param pokemon_id - The id of the pokemon to get.
    @param request - The request for this request. Used to pass session and session factory.

    @return The requested pokemon or ` HTTPException `
    """
    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        async with session.begin():
            pokemon = await session.execute(
                select(Pokemon)
                .filter(Pokemon.id == pokemon_id)
                .order_by(Pokemon.id)
                .options(selectinload(Pokemon.types)),
            )

            pokemon = pokemon.scalars().first()

            return pokemon


@router.get("/pokemon/type/{type_id}")
async def get_pokemon_by_type_id(type_id: int, request: Request):
    """
    Get pokemon by type id. This is a helper method for get_pokemon_by_type.

    @param type_id - The id of the type to get the pokemon for.
    @param request - The request for this request. Used to get the session factory.

    @return A list of pokemon matching the type id
    """
    async_session = request.app.state.db_session_factory
    async with async_session() as session:
        pokemon_query = (
            select(Pokemon)
            .join(Pokemon.types)
            .filter(PokeType.id == type_id)
            .options(
                selectinload(Pokemon.types),
            )  # Optionally eager load associated types
        )
        pokemon_list = await session.execute(pokemon_query)
        pokemons = pokemon_list.scalars().all()
        return pokemons
