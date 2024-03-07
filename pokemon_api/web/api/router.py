from fastapi.routing import APIRouter

from pokemon_api.web.api import monitoring, pokemons

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(pokemons.router)
