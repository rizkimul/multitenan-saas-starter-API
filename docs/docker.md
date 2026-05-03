# Docker & Infrastructure Setup

## Why Start With Infrastructure

`docker-compose.yml` defines every service your app depends on — Postgres,
Redis, the app container. Getting this right first forces concrete decisions
about service names and ports before writing any Python. Everything else
references these names.

## `depends_on` with Health Checks

```yaml
depends_on:
  db:
    condition: service_healthy
```

`condition: service_started` (the default) only waits for the container to
exist. `condition: service_healthy` waits for the health check to pass — i.e.,
Postgres is actually ready to accept connections. Without this, the app
container starts before Postgres finishes initializing and crash-loops.

## `uv` in the Dockerfile

`uv` (from the Ruff/Astral team) is a modern Python package installer —
10–100x faster than pip. Using it in the Dockerfile speeds up image rebuilds
significantly. Worth knowing for any modern Python project.

## DATABASE_URL Is Not in `.env`

`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` are in `.env` as separate
values. The full `DATABASE_URL` is assembled inside `core/config.py` via a
Pydantic validator. This avoids duplicating credentials and keeps the URL
construction in one authoritative place.

## `--reload` in Compose, Not in Dockerfile CMD

```yaml
# docker-compose.yml — local dev only
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Dockerfile CMD — production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The Docker image is built once and used in both environments. Compose
overrides the CMD for local dev. You deploy the same image to prod without
the reload flag.

## Concepts to Research

- Docker multi-stage builds (for slimmer production images)
- `HEALTHCHECK` instruction in Dockerfile vs compose healthcheck
- Docker layer caching — why `COPY pyproject.toml .` comes before `COPY . .`
