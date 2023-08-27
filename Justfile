
# Load environment variables using 1password-cli
opornone := if `hash op &> /dev/null && echo found` == "found" { "op run --env-file .env --" } else { "" }

# List commands
default:
  @just --list

# Set up poetry/python environment
init:
  pre-commit install
  pre-commit autoupdate
  poetry install

# Run linters linters
lint:
  poetry run ruff check .
  poetry run mypy firefox_to_sqlite
  poetry run black . --check

# Run pytest with supplied options
@test *options:
  poetry run pytest --cov=firefox_to_sqlite {{options}}
  poetry run coverage html

# Run linters in fix mode
fix:
  poetry run ruff check . --fix
  poetry run black .

# Build docs
docs *type:
  poetry run {{ if type == "live" { "sphinx-autobuild" } else { "sphinx-build" } }} -b html docs docs/_build/html

# Enter virtual environment
shell:
  poetry shell

# Publish package to PyPI
publish:
  # Using PyPI token from POETRY_PYPI_TOKEN_PYPI
  # Build package
  poetry build
  # Publish package
  {{opornone}} poetry publish

docker_socket := `docker context inspect --format '{{.Endpoints.docker.Host}}'`
docker_status := `limactl ls --json | jq -r 'select(.name == "docker") | .status'`

# act shortcut
act *options:
  [[ {{docker_status}} == "Running" ]] || limactl start docker
  act --container-daemon-socket {{docker_socket}} {{options}}
