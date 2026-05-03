# Python Project Setup

## Why `pyproject.toml` Over `requirements.txt`

`pyproject.toml` is the modern Python standard (PEP 517/518). It replaces:
- `requirements.txt` — dependencies
- `setup.cfg` / `setup.py` — package metadata
- `pytest.ini` — pytest config
- `.ruff.toml`, `mypy.ini` — tool configs

One file, one source of truth. Every serious Python project uses it now.

## Dependency Choices

### `fastapi[standard]`
The `[standard]` extra bundles `uvicorn`, `httpx`, `python-multipart`, and
`email-validator`. You get a production-ready server without extra installs.

### `sqlalchemy[asyncio]` + `asyncpg`
SQLAlchemy 2.0 ships async support as an optional extra. `asyncpg` is the
fastest async PostgreSQL driver for Python. The two are used together:
SQLAlchemy handles the ORM layer, asyncpg handles the actual wire protocol.

### `PyJWT` over `python-jose`
`python-jose` is largely unmaintained and has known CVEs. `PyJWT` is actively
maintained, simpler, and the correct choice for new projects in 2024+.

### `passlib[bcrypt]`
`passlib` provides a clean abstraction over password hashing algorithms.
The `[bcrypt]` extra adds bcrypt support, which is the standard for secure
password hashing. Research: why bcrypt is preferred over SHA-256 for passwords
(hint: it's intentionally slow).

### `pydantic-settings`
Pydantic v2 moved settings management into a separate package. It reads
env vars and `.env` files and validates them as typed Python objects.
This is how we avoid hardcoding secrets.

## Dev Dependencies

| Package | Purpose |
|---------|---------|
| `pytest-asyncio` | Runs async test functions natively |
| `httpx` | Async HTTP client — used as the FastAPI test client |
| `ruff` | Linter + formatter (replaces flake8, isort, black) |
| `mypy` | Static type checker |
| `pytest-cov` | Coverage reports |

## `asyncio_mode = "auto"` in pytest config

Without this, every async test function needs `@pytest.mark.asyncio`.
With `auto` mode, pytest-asyncio detects `async def test_*` functions
automatically. Less boilerplate, no forgotten decorator bugs.

## The `lifespan` Pattern in `app/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # everything before yield = startup
    yield
    # everything after yield = shutdown
```

FastAPI replaced `@app.on_event("startup")` with the `lifespan` context
manager (PEP 567 / Starlette 0.20+). The old event decorators still work
but are deprecated. Always use `lifespan` in new projects.

We start with an empty lifespan — we'll add DB pool init and Redis connection
here as we build those layers.

## `__init__.py` Files

Each folder has an empty `__init__.py` to make it a Python package. This
enables imports like `from app.services.user import UserService`. Without it,
Python won't recognize the folder as importable.

## Concepts to Research

- PEP 517/518 — the build system standard behind pyproject.toml
- Hatchling — the build backend we use (alternative to setuptools)
- Why bcrypt is slow by design (key stretching)
- JWT structure: header.payload.signature — what each part contains
- `AsyncGenerator` type hint — how Python's async context managers work
