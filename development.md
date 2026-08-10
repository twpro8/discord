# Lumiere Development

## Getting Started

Before starting the development environment, create a local environment file:

```bash
cp .env.example .env
```

Then start the local development stack with Docker Compose:

```bash
docker compose watch
```

Now you can open your browser and interact with these URLs:

| Name                                                             | URL                          |
|------------------------------------------------------------------|------------------------------|
| Frontend, built with Docker                                      | <http://localhost:5173>      |
| Backend (JSON API with OpenAPI documentation)                    | <http://localhost:8000>      |
| Automatic Interactive Docs (Swagger UI)                          | <http://localhost:8000/docs> |
| Adminer, database web administration                             | <http://localhost:8080>      |
| Mailcatcher                                                      | <http://localhost:1080>      |
| Traefik UI, to see how the routes are being handled by the proxy | <http://localhost:8090>      |

**Note**: The first time you start the stack, it might take a minute or more for it to be ready. While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run (in another terminal):

```bash
docker compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker compose logs backend
```

## Mailcatcher

Mailcatcher is a simple SMTP server that catches all emails sent by the backend during local development. Instead of sending real emails, they are captured and displayed in a web interface.

This is useful for:

* Testing email functionality during development
* Verifying email content and formatting
* Debugging email-related functionality without sending real emails

The backend is automatically configured to use Mailcatcher when running with Docker Compose locally (SMTP server running on port 1025). All captured emails can be viewed at <http://localhost:1080>.

## Local Development

The Docker Compose files are configured so that each service is available on a different port in `localhost`.

For the backend, it uses the same port that would be used by its local development server, so, the backend is at `http://localhost:8000`.

This way, you could turn off a Docker Compose service and start its local development service, and everything would keep working, because it all uses the same ports.

For example, you can stop the `frontend` service in the Docker Compose, in another terminal, run:

```bash
docker compose stop frontend
```

And then start the local frontend development server:

```bash
pnpm run dev
```

Or you could stop the `backend` Docker Compose service:

```bash
docker compose stop backend
```

And then you can run the local development server for the backend:

```bash
cd backend
uv run uvicorn src.main:app --reload
```

## Docker Compose files and env vars

There is a main `compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

After changing any environment variables, restart the stack:

```bash
docker compose watch
```

## Voice calls: TURN server (production)

Voice calling works over STUN alone for most home/office networks with no
extra setup — the backend's `GET /api/v1/calls/turn-credentials` endpoint
returns STUN-only ICE servers by default (`STUN_URLS` in `.env`).

For reliable connectivity behind symmetric NATs or restrictive corporate
firewalls, a TURN relay is needed. A self-hosted `coturn` service is
defined in `compose.yml`, gated behind the `turn` Compose profile so it
doesn't start by default:

```bash
docker compose --profile turn up -d coturn
```

Then set in `.env`:

```
TURN_URLS=turn:your-domain:3478
TURN_SECRET_KEY=<a strong random secret>
```

Two things this repo's Compose setup cannot do for you, since they're
host/network infrastructure rather than application config:

* **Firewall/port-forwarding**: open UDP+TCP `3478` (the TURN listener)
  and the UDP relay range `49152-49252` on the host firewall or cloud
  security group. `coturn` runs with `network_mode: host` (required for
  ICE relay candidates to be reachable at the host's real IP), so it is
  **not** routed through Traefik — Traefik only proxies HTTP(S), not a
  raw UDP port range.
* **Single-host constraint**: `network_mode: host` means `coturn` only
  makes sense on a single host. If this stack ever moves to multi-host or
  managed Kubernetes, swap to a managed TURN provider that supports the
  same REST-API HMAC credential scheme (`TURN_URLS`/`TURN_SECRET_KEY`) —
  no backend code changes needed either way.

To verify TURN is actually working, feed the response of
`GET /api/v1/calls/turn-credentials` (while logged in) into the public
[Trickle ICE](https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice)
test page and confirm `relay`-typed candidates are gathered, or check
`docker compose logs coturn` for allocate/permission requests during a
real call.

## Observability: Grafana, Prometheus, Loki

Centralized backend logs and basic HTTP metrics are available through
Grafana, opt-in via the `observability` Compose profile (it doesn't start
with a plain `docker compose watch`, to keep the default stack lean):

```bash
docker compose --profile observability up -d
```

| Name                                                     | URL                        |
|-----------------------------------------------------------|----------------------------|
| Grafana                                                    | <http://localhost:3000>    |
| Prometheus                                                 | <http://localhost:9090>    |
| Loki (API only, query through Grafana)                     | <http://localhost:3100>    |

Log in to Grafana with `GF_SECURITY_ADMIN_USER`/`GF_SECURITY_ADMIN_PASSWORD`
from `.env` (defaults to `admin`/`changethis` — **change this for any real
deployment**, same as `JWT_SECRET_KEY`/`POSTGRES_PASSWORD`). Both the
Prometheus and Loki datasources, and a starter **Lumiere FastAPI Backend**
dashboard (request rate, latency percentiles, status code breakdown,
4xx/5xx error rate, log volume by level, and a live logs panel), are
auto-provisioned — no manual setup needed.

**How it works**: the backend always exposes `GET /metrics`
(`prometheus-fastapi-instrumentator`), scraped by Prometheus every 15s.
Backend/worker container logs (JSON via `LOG_FORMAT=json`, set for both
containers regardless of whether this profile is running) are tailed by
Grafana Alloy straight from the Docker socket — filtered to just those two
services — and pushed to Loki. Only Grafana gets a public Traefik route in
production (`grafana.${DOMAIN}`, gated by its own login, same pattern as
`adminer`); Prometheus/Loki/Alloy are never routed externally, reachable
only from other containers on the same Docker network.

To verify logs/metrics are flowing:

```bash
# Generate some traffic, then:
curl http://localhost:8000/metrics | grep http_requests_total
curl -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service_name="backend"}'
```

or just open Grafana → Explore → Loki and run `{service_name=~"backend|worker"}`.

**Retention**: Loki keeps logs for 14 days (`observability/loki/loki-config.yml`).
Prometheus/Grafana use default retention with persistent named volumes
(`prometheus-data`, `loki-data`, `grafana-data`) so data survives container
restarts. None of this affects the app itself — the backend and worker run
identically whether or not the `observability` profile is up; the only
things that would notice Prometheus/Loki/Grafana being down are Grafana's
own dashboards showing stale/no data.

## Git Hooks

This project uses `prek`, a modern, Rust-based alternative to `pre-commit`, to run checks before each commit.

Install the Git hooks after cloning the repository:

```bash
uv run prek install -f
```

The `-f` flag forces the installation, in case there was already a `pre-commit` hook previously installed.

You can also run all configured hooks manually:

```bash
uv run prek run --all-files
```

Example output:

```text
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
typos....................................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
mypy check...............................................................Passed
Generate Frontend SDK....................................................Passed
```

Using `prek` ensures that formatting, linting, type checking, frontend SDK generation, and other automated checks are applied consistently before changes are committed.

`prek` also installs a `commit-msg` hook that enforces [Conventional Commits](https://www.conventionalcommits.org/) formatting (`feat: ...`, `fix(scope): ...`, etc.) — see [Versioning & releases](#versioning--releases) below for why. If you installed the Git hooks before this was added, re-run `uv run prek install -f` to pick up the new hook type; otherwise the commit-msg check won't actually run locally (it'll still be enforced in CI via the same commit history that drives releases).

## Versioning & releases

Lumiere's version is bumped and `CHANGES.md` is updated automatically by [python-semantic-release](https://python-semantic-release.readthedocs.io/), based on Conventional Commit messages merged into `main`. There's no manual version bumping or changelog editing.

- **Canonical version:** `backend/pyproject.toml`'s `[project].version` is the version to look at day-to-day (and what `uv`/`hatchling` build against). `frontend/package.json`, `frontend/src-tauri/tauri.conf.json`, and `frontend/src-tauri/Cargo.toml` are kept in sync automatically on every release. The backend also exposes its running version at `/api/v1/health` and in the `/docs` OpenAPI schema.
- **How releases happen:** every push to `main` (i.e. every `dev` → `main` merge) is evaluated by `.github/workflows/release.yml`. If there are releasable commits since the last tag (any `feat`/`fix`/breaking-change commit), it computes the next version, updates all version files and `CHANGES.md`, tags the commit, and publishes a GitHub Release — fully automatically. If there's nothing releasable (e.g. only `chore`/`docs`/`ci` commits), it's a no-op.
- **Commit messages drive this directly**, which is why they're enforced by the `commit-msg` hook above: `feat:` bumps minor, `fix:` bumps patch, a `!` after the type/scope (e.g. `feat(auth)!: ...`) or a `BREAKING CHANGE:` footer bumps... also minor for now, since the project is pre-1.0 and breaking changes intentionally don't jump straight to `1.0.0`.
- **"Unreleased" work** is just whatever's on `dev` (or an open PR) that hasn't been merged to `main` yet — there's no separate "Unreleased" section in `CHANGES.md`; every entry in it is already released.
- Don't hand-edit the version in any of the four files above, and don't hand-edit `CHANGES.md` — both are bot-managed.
