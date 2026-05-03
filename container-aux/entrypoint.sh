#!/bin/sh

set -eux

# run migrations before every startup, will be no-op if already applied
uv run python3 manage.py migrate

caddy run --config /app/container-aux/Caddyfile &
uv run gunicorn --bind 0.0.0.0:8100 bctf.wsgi &
uv run gunicorn --bind 0.0.0.0:8101 bctf-api.wsgi &

wait -n
exit $?
