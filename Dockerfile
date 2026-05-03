FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1

WORKDIR /app
USER app

# Sync the project into a new environment, asserting the lockfile is up to date
COPY pyproject.toml uv.lock /app
RUN uv sync --locked

# Copy the project into the image
COPY . /app

ARG APP=bctf.asgi
ENV APP=${APP}

EXPOSE 8000
CMD uv run gunicorn --bind 0.0.0.0:8000 $APP
