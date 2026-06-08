# python-postgres-demo

A small Python repository that demonstrates:

- project-local virtual environment management with `uv`
- `src/` package layout
- formatting with Black
- linting with Ruff
- static typing with MyPy
- PostgreSQL connectivity using `psycopg`
- basic tests with `pytest`

## Quick start

## uv install

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path += ";$HOME\.local\bin"
uv --version

### 1) Create the environment

```bash
uv venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
uv sync --all-extras --dev
```

### 3) Configure database settings

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials.

### 4) Run checks

```bash
uv run black --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

### 5) Test the database connection

```bash
uv run python -m postgres_demo.cli
```

## Notes

- The code uses a `src/` layout to avoid accidental imports from the project root.
- Configuration is centralized in `pyproject.toml`.
- Database settings are loaded from environment variables.
- The connection pool is created lazily and can be closed cleanly.
