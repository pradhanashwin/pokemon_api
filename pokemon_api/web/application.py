from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from pokemon_api.web.api.v1.router import api_router
from pokemon_api.web.lifetime import register_shutdown_event, register_startup_event


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="pokemon_api",
        version=metadata.version("pokemon_api"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api/v1")
    # After creating new version of APIs simply add like this
    # app.include_router(router=api_router, prefix="/api/v2") # noqa E800

    return app
