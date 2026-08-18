# beavercds-frontend

Frontend / Scoreboard for Jeopardy-style CTFs. Meant to be run alongside and
integrates with <https://github.com/osusec/beavercds-backend> challenge
deployment tooling.

## Developing

The `docker-compose.yaml` sets up a local development instance with automatic
hot-reloading and the Django development server.

Requirements:

- Docker/Podman
- docker-compose >= 2.22.0 (for watch)

Build, run, and sync changes into the running containers with `docker-compose
watch` (note, this runs in the foreground!). Django will then be available at
<https://bctf.localhost> with self-signed certs.

The `watch` hot-reload will _not_ run migrations if they change. When needed,
re-run migrations by manually stopping and restarting the project:
`docker-compose down && docker-compose up`.

If you need to test a different domain name:

- change the `caddy:` label for the `bctf` and `bctf-api` containers from
  `bctf.localhost` to your domain name.
- update `BCTF_ALLOWED_HOSTS` envvar on the `bctf` container.
