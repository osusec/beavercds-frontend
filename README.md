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

Build and start the containers with `docker-compose up -d --build`. Django will
then be available at <https://bctf.localhost> with self-signed certs.

### Hot-reload cycle

For hot-reload support, use `docker-compose watch`. This will build and start
the containers if not already running, and sync file changes into the containers
on change for Django's hot-reload. 

The `watch` hot-reload will _not_ run migrations if they change. When needed,
re-run migrations by manually stopping and restarting the migrations job
container: `docker-compose down migrations && docker-compose up -d`.

> [!NOTE]
> `docker-compose watch` runs in the foreground while it is watching! The
> containers it starts are started as if with `up -d`, so interrupting watch
> will not automatically bring them down.

If you need to test a different domain name:

- change the `caddy:` label for the `bctf` and `bctf-api` containers from
  `bctf.localhost` to your domain name.
- update `BCTF_ALLOWED_HOSTS` envvar on the `bctf` container.

### Customizing settings

To add additional environment variables, create a `.env` file with config OR
edit the compose file `environment:` block for the `bctf` container.

Envvars defined inline in the docker-compose take precedence over `.env`.
