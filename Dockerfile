FROM python:3.12-alpine as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Use copy mode since the cache and build filesystem are on different volumes.
ENV UV_LINK_MODE=copy

# Prevent Python from writing .pyc files to disk.
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr so logs appear immediately.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies into the uv venv using cache and bind mounts so neither
# uv nor the lock files need to be copied into the image.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# ------

# Development image for local docker-compose development. Intended to be used
# with Compose Watch for dev server hot-reload.
FROM builder AS development

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

# Default to bctf app but allow overriding for bctf-api via envvar.
ARG APP=bctf
ENV APP=${APP}

CMD python manage.py runserver --settings ${APP}.settings 0.0.0.0:8000

# ------

# Production image using proper gunicorn WSGI.
FROM python:3.12-alpine AS production

# Prevent Python from buffering stdout/stderr so logs appear immediately.
ENV PYTHONUNBUFFERED=1
# Activate the virtual environment copied from the build stage.
ENV PATH="/app/.venv/bin:$PATH"

# Run production as a non-root user
RUN addgroup -g 1000 nonroot && \
    adduser -u 1000 -G nonroot -D nonroot

# USER before WORKDIR means the directory is created with the proper non-root
# ownership.
USER nonroot
WORKDIR /app

# Copy only the pre-built venv and app source files.
COPY --from=builder /app/.venv /app/.venv
COPY . .

EXPOSE 8000

# Default to bctf app but allow overriding for bctf-api via envvar.
ARG APP=bctf
ENV APP=${APP}

# Run Gunicorn as the production WSGI server.
CMD gunicorn "${APP}.wsgi" --bind "0.0.0.0:8000"
