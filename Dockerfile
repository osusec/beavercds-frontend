FROM python:3.12-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add caddy tini

# Disable development dependencies
ENV UV_NO_DEV=1
ENV PYTHONUNBUFFERED=1

RUN adduser -S -s /sbin/nologin bctf

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

COPY pyproject.toml uv.lock /app
RUN uv sync --locked

# Copy the project into the image
COPY . /app

RUN chown -R bctf /app
USER rctf

EXPOSE 8000
EXPOSE 8001
CMD ["tini", "-g", "--", "/app/container-aux/entrypoint.sh"]
