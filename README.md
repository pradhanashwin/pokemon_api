# pokemon_api

This project was generated using fastapi_template.

## Project structure

```bash
$ tree "pokemon_api"
pokemon_api
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
│       └── pokemon.py  # All the table related to pokemons.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── pokemons  # Endpoints directory for pokemons.
    │   │   └── views.py  # Different routes to get pokemons data.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory or rename
`example.env` to `.env` and place all
environment variables here

All environment variables should start with "POKEMON_API_" prefix.

For example if you see in your "pokemon_api/settings.py" a variable named like
`random_parameter`, you should provide the "POKEMON_API_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `pokemon_api.settings.Settings.Config`.

An example of .env file:
```bash
POKEMON_API_RELOAD="True"
POKEMON_API_PORT="8000"
POKEMON_API_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/
## Warning

**Attention:** Please make sure to set up the required environment variables or configuration files before running the application. Failure to provide these settings may result in errors during application startup.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

## Installation

### Using virtual environment
**Create a virtual environment and install dependencies using Conda**

1. Create a New Conda Environment:

   Open your terminal or command prompt and use the following command to create a new Conda environment. Replace `myenv` with the name you'd like to give to your environment.

   ```shell
   conda create --name pokemon_api python=3.8
   ```

   This command will create a new Conda environment named `pokemon_api` and use Python 3.8.

2. Activate the Conda Environment**:

   Once the environment is created, activate it using the following command:

   ```shell
   conda activate pokemon_api
   ```

   Replace `pokemon_api` with the name of your Conda environment.

After you activated the enviroment install the dependencies using poetry.

```bash
pip install poetry
poetry install
poetry run python -m pokemon_api
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/


## Using Docker

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```


## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* isort (sorts imports in all files);
* flake8 (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/



### Using Docker

You can start the project with Docker using the following command:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . run --build --rm api pytest -vv .
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . down
```
This command will start the server on port 8000.



For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=pokemon_api" -e "POSTGRES_USER=pokemon_api" -e "POSTGRES_DB=pokemon_api" postgres:13.8-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```
