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

For example, you can stop the `backend` service in the Docker Compose, in another terminal, run:

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
