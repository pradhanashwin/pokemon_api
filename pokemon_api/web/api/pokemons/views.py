from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from pokemon_api.db.models.pokemon import Pokemon, PokeType
from pokemon_api.web.lifetime import get_type

router = APIRouter()


@router.get("/pokemon")
async def get_pokemon(
    request: Request,
    pokemon_id: int = Query(None, description="Filter by Pokémon ID"),
    name: str = Query(None, description="Filter by Pokémon name"),
):
    """
    Get a Pokémon by ID or name.

    @param pokemon_id: Optional. Filter by Pokémon ID.
    @param name: Optional. Filter by Pokémon name.
    @param request: The request for this request. Used to pass session and session factory.

    @return: The requested Pokémon or `HTTPException`.
    """
    if pokemon_id is None and name is None:
        raise HTTPException(
            status_code=400,
            detail="Either Pokemon ID or name must be provided.",
        )

    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        if pokemon_id is not None:
            pokemon_query = (
                select(Pokemon)
                .filter(Pokemon.id == pokemon_id)
                .options(selectinload(Pokemon.types))
            )
        else:
            if name is None:
                raise HTTPException(
                    status_code=400,
                    detail="Pokemon ID or name must be provided.",
                )
            pokemon_query = (
                select(Pokemon)
                .filter(Pokemon.name.ilike(f"%{name}%"))
                .options(selectinload(Pokemon.types))
            )

        pokemon = await session.execute(pokemon_query)
        pokemon = pokemon.scalars().first()

        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")

        return pokemon


@router.get("/pokemon/type")
async def get_pokemon_by_type(
    request: Request,
    type_id: int = Query(None, description="Filter by type ID"),
    type_name: str = Query(None, description="Filter by type name"),
):
    """
    Get Pokémon by type ID or type name.

    @param type_id: Optional. Filter by type ID.
    @param type_name: Optional. Filter by type name.
    @param request: The request for this request. Used to pass session and session factory.

    @return: A list of Pokémon matching the type ID or name.
    """
    if type_id is None and type_name is None:
        raise HTTPException(
            status_code=400,
            detail="Either type ID or name must be provided.",
        )

    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        if type_id is not None:
            pokemon_query = (
                select(Pokemon)
                .join(Pokemon.types)
                .filter(PokeType.id == type_id)
                .options(selectinload(Pokemon.types))
            )
        else:
            if type_name is None:
                raise HTTPException(
                    status_code=400,
                    detail="Type ID or name must be provided.",
                )
            pokemon_query = (
                select(Pokemon)
                .join(Pokemon.types)
                .filter(PokeType.name.ilike(f"%{type_name}%"))
                .options(selectinload(Pokemon.types))
            )

        pokemon_list = await session.execute(pokemon_query)
        pokemons = pokemon_list.scalars().all()

        if not pokemons:
            raise HTTPException(status_code=404, detail="Pokémon not found")

        return pokemons


@router.post("/pokemon")
async def create_pokemon(pokemon_data: dict, request: Request):
    """
    Create a new Pokémon.

    @param pokemon_data: Data of the Pokémon to be created.
    @param request: The request for this request. Used to pass session and session factory.

    @return: The created Pokémon.
    """
    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        # Extract data from the request
        pokemon_id = pokemon_data.get("id")
        name = pokemon_data.get("name")
        types_data = pokemon_data.get("types")
        images = pokemon_data.get("images")

        # Check if required data is provided
        if not pokemon_id or not name or not types_data or not images:
            raise HTTPException(
                status_code=400,
                detail="Incomplete data provided for creating Pokémon.",
            )

        # Get type IDs and instances
        types = [typ["name"] for typ in types_data]
        type_ids, type_instances = await get_type(types, session)

        # Create a new Pokémon instance
        new_pokemon = Pokemon(
            id=pokemon_id,
            name=name,
            images=images,
            types=type_instances,
        )

        # Add the new Pokémon to the session and commit changes
        session.add(new_pokemon)
        await session.commit()

        return new_pokemon


@router.put("/pokemon/{pokemon_id}")
async def update_pokemon(pokemon_id: int, pokemon_data: dict, request: Request):
    """
    Update an existing Pokémon.

    @param pokemon_id: The ID of the Pokémon to be updated.
    @param pokemon_data: Data of the Pokémon to be updated.
    @param request: The request for this request. Used to pass session and session factory.

    @return: The updated Pokémon.
    """
    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        # Extract data from the request
        name = pokemon_data.get("name")
        types_data = pokemon_data.get("types")
        images = pokemon_data.get("images")
        if types_data:
            types = [typ["name"] for typ in types_data]
            type_ids, type_instances = await get_type(types, session)
        # Retrieve the Pokémon to be updated from the database
        pokemon_query = (
            select(Pokemon)
            .filter(Pokemon.id == pokemon_id)
            .options(selectinload(Pokemon.types))
        )
        pokemon = await session.execute(pokemon_query)
        pokemon = pokemon.scalars().first()

        # Check if the Pokémon exists
        if not pokemon:
            raise HTTPException(
                status_code=404,
                detail=f"Pokémon with id {pokemon_id} not found",
            )

        # Update the Pokémon's attributes if new data is provided
        if name:
            pokemon.name = name

        pokemon.types = type_instances
        if images:
            pokemon.images = images

        # Commit the changes to the database
        await session.commit()

        return pokemon


@router.delete("/pokemon/{pokemon_id}")
async def delete_pokemon(pokemon_id: int, request: Request):
    """
    Delete an existing Pokémon.

    @param pokemon_id: The ID of the Pokémon to be deleted.
    @param request: The request for this request. Used to pass session and session factory.

    @return: A message indicating the deletion status.
    """
    async_session = request.app.state.db_session_factory

    async with async_session() as session:
        # Retrieve the Pokémon to be deleted from the database
        pokemon = await session.execute(
            select(Pokemon).filter(Pokemon.id == pokemon_id),
        )
        pokemon = pokemon.scalars().first()

        # Check if the Pokémon exists
        if not pokemon:
            raise HTTPException(
                status_code=404,
                detail=f"Pokémon with id {pokemon_id} not found",
            )

        # Delete the Pokémon from the database
        session.delete(pokemon)

        # Commit the changes to the database
        await session.commit()

    return {"message": f"Pokémon with id {pokemon_id} has been deleted"}
