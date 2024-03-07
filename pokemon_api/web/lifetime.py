import asyncio
import random
from typing import Awaitable, Callable

import httpx
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from pokemon_api.db.meta import meta
from pokemon_api.db.models import load_all_models
from pokemon_api.db.models.pokemon import (
    Base,
    PokeGeneration,
    Pokemon,
    PokeMove,
    PokeType,
)
from pokemon_api.db.utils import create_database
from pokemon_api.settings import settings

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


async def get_type(type_data: list, session: AsyncSession) -> list:
    """
    Get Type ids and instances based on type_data.

    @param type_data - List of types to get.
    If there are types not found in the database they will be created
    @param session - SQLAlchemy session to use for
    """
    type_ids = []
    type_instances = []
    # async with session.begin():
    # Find the Type instance with the given name in the type_data.
    async with session.begin():
        for type_name in type_data:
            # Query the database to find the Type with the given name
            type_instance = await session.execute(
                select(PokeType).filter_by(name=type_name),
            )
            type_instance = type_instance.scalars().first()
            # Create a new Type instance and add it to the database
            if type_instance is None:
                # If type not found, create a new Type instance and add it to the database
                type_instance = PokeType(name=type_name)
                session.add(type_instance)
            type_ids.append(type_instance.id)
            type_instances.append(type_instance)
        await session.commit()  # Commit all changes made within the transaction
    return type_instances


async def get_generation_by_url(
    generation_dict: dict,
    session: AsyncSession,
) -> PokeGeneration:
    """
    Get Generation instance based on a generation URL.

    @param generation_url - Generation URL to get.
    If the generation is not found in the database, it will be created
    @param session - SQLAlchemy session to use
    """
    # Extract generation name from the URL
    generation_name = generation_dict["name"]
    async with session.begin():
        # Query the database to find the Generation with the given name
        generation_instance = await session.execute(
            select(PokeGeneration).filter_by(name=generation_name),
        )
        generation_instance = generation_instance.scalars().first()

        # Create a new Generation instance and add it to the database if not found
        if generation_instance is None:
            async with httpx.AsyncClient() as client:
                generation_response = await client.get(generation_dict["url"])
                generation_data = generation_response.json()
                generation_instance = PokeGeneration(
                    name=generation_name,
                    id=generation_data["id"],
                    region=generation_data["main_region"]["name"],
                )
            session.add(generation_instance)

        await session.commit()  # Commit all changes made within the transaction

    return generation_instance


async def get_moves(move_data: list, session: AsyncSession) -> list:
    """
    Get Move IDs and instances based on move_data.

    @param move_data - List of moves to get.
    If there are moves not found in the database they will be created
    @param session - SQLAlchemy session to use for database operations
    """
    move_ids = []
    move_instances = []

    async with session.begin():
        for move_name in move_data:
            # Query the database to find the Move with the given name
            move_instance = await session.execute(
                select(PokeMove).filter_by(name=move_name),
            )
            move_instance = move_instance.scalars().first()

            # Create a new Move instance and add it to the database if not found
            if move_instance is None:
                move_instance = PokeMove(name=move_name)
                session.add(move_instance)

            move_ids.append(move_instance.id)
            move_instances.append(move_instance)

        await session.commit()  # Commit all changes made within the transaction
    return move_instances


async def save_pokemon(response: dict, session: AsyncSession) -> None:
    """
    Save Pokemon Spritings and Types to the database. This is a helper function for : py : func : ` ~asyncio. read_pokemon `.

    @param response - The response from the API
    @param session - The session to use for the database operations ( if any
    """
    pokemon_id = response["id"]
    name = response["name"]
    is_legendary = response["is_legendary"]
    types = [typ["type"]["name"] for typ in response["types"]]
    # Find the PokeType with the given name in the database.
    type_instances = await get_type(types, session)

    # randomly select 4 moves if length of moves if > 4
    if len(response["moves"]) > 4:
        selected_moves = random.sample(response["moves"], 4)
    else:
        selected_moves = response["moves"]
    moves = [(mv["move"]["name"]) for mv in selected_moves]
    # Find the PokeMove with the given name in the database.
    move_instances = await get_moves(moves, session)
    generation = await get_generation_by_url(response["generation"], session)

    images = {
        "front_default": response["sprites"]["front_default"],
        "back_default": response["sprites"]["back_default"],
    }

    # Create a new Pokemon instance and add it to the database
    new_pokemon = Pokemon(
        id=pokemon_id,
        name=name,
        images=images,
        is_legendary=is_legendary,
        generation=generation,
    )
    # Associate types with the new Pokemon instance
    new_pokemon.types = type_instances
    # Associate moves with the new Pokemon instance
    new_pokemon.moves = move_instances

    session.add(new_pokemon)
    await session.commit()  # Commit changes made within the transaction


async def populate_database(engine) -> None:
    """
    Populates pokemon database with data from API. This is a blocking call.

    @param engine - SQLAlchemy engine to use for database queries
    """
    async with engine.begin():
        async with httpx.AsyncClient() as client:
            poke_url = f"{POKEAPI_BASE_URL}/pokemon?limit=500"
            # This function will fetch the pokemon data from the pokemon and save it to the database. # noqa
            while poke_url:
                response = await client.get(poke_url)
                data = response.json()
                async with AsyncSession(engine, expire_on_commit=False) as session:
                    # Retrieve the pokemon data from the server.
                    for result in data["results"]:
                        detail_path = result["url"]
                        detail_response = await client.get(detail_path)
                        detail_data = detail_response.json()
                        species_detail = await client.get(detail_data["species"]["url"])
                        species_data = species_detail.json()
                        # Merge dictionary of responses
                        complete_detail = {**detail_data, **species_data}
                        # Save the pokemon data to the database.
                        if detail_data:
                            await save_pokemon(complete_detail, session)
                poke_url = data.get("next")
                # Introduce a delay of 1 second between requests
                await asyncio.sleep(1)
                # TODO: make api call more efficient because the pokeapi throttles the response after 500 requests
                # for now  ending the loop. remove poke_url = False to run code until response is empty
                poke_url = False


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _create_tables() -> None:
    await create_database()
    load_all_models()
    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
    async with engine.begin() as connection:
        try:
            # Check if the Pokemon table exists
            await connection.execute(select(Pokemon))
        except NoSuchTableError:
            # Create the Pokemon table if it doesn't exist
            await meta.pokemon.create(engine)

        await populate_database(engine)

    await engine.dispose()


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        _setup_db(app)
        await _create_tables()
        app.middleware_stack = app.build_middleware_stack()
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()

        pass  # noqa: WPS420

    return _shutdown
