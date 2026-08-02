# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Codex CLI, Cursor, OpenCode, etc.) when working with code in this repository.

## Project overview

Lumiere is a real-time chat application: a FastAPI backend (Python 3.14) and a React 19 frontend (TanStack Router/Query), backed by Postgres and Redis, run together via Docker Compose.

## Commands

### Environment setup

```bash
cp .env.example .env               # first-time setup, from repo root
docker compose watch               # start full stack (backend, frontend, db, redis, mailcatcher, adminer, traefik)
```

Local URLs: frontend `:5173`, backend `:8000` (docs at `/docs`), Adminer `:8080`, Mailcatcher `:1080`, Traefik UI `:8090`.

You can stop an individual Compose service and run it natively while the rest of the stack keeps working (same ports), e.g. `docker compose stop backend` then run the backend commands below directly.

### Backend (`backend/`, managed with `uv`)

```bash
cd backend
uv run uvicorn src.main:app --reload         # run dev server natively

bash scripts/lint.sh                          # mypy (strict) + ruff check + ruff format --check
bash scripts/format.sh                        # ruff check --fix + ruff format
bash scripts/test.sh                          # prestart (migrations) + pytest + coverage report/html

uv run pytest tests/                          # run tests directly
uv run pytest tests/integration/chats -k test_name   # single test/module
uv run pytest tests/unit                      # unit tests only

uv run alembic revision --autogenerate -m "message"  # new migration
uv run alembic upgrade head                          # apply migrations
```

Tests require `ENVIRONMENT=testing` and a running Postgres + Redis (see `.env.test`, `pytest.ini` loads `../.env.test` then `../.env`). `tests/conftest.py` overrides the DB session and Redis client dependencies, drops/recreates all tables, and seeds data (`tests/seeder.py`) once per session. Tests are split into `tests/unit/`, `tests/integration/<module>/`, `tests/e2e/`.

### Frontend (`frontend/`, managed with `pnpm`)

```bash
pnpm install
pnpm run dev            # Vite dev server, proxies /api -> localhost:8000
pnpm run build           # tsc -b && vite build
pnpm run lint            # oxlint
pnpm run format          # prettier --write (also sorts imports)
pnpm run format:check
pnpm run test            # vitest run
pnpm run test:watch      # vitest watch
```

From the repo root, `pnpm run dev` / `pnpm run lint` / `pnpm run generate-client` proxy to the frontend workspace.

### Cross-cutting

```bash
bash scripts/generate-client.sh   # regenerate frontend/openapi.json + typed API client from the backend's live OpenAPI schema
uv run prek install -f            # install git hooks (prek = Rust pre-commit alternative)
uv run prek run --all-files       # run all hooks manually (typos, ruff, mypy, SDK generation, zizmor)
```

The `generate-frontend-sdk` pre-commit hook regenerates the client automatically whenever `backend/**` changes — after editing backend routes/schemas, either let the hook run on commit or run `scripts/generate-client.sh` manually before relying on frontend types.

Dependency changes (`pyproject.toml`, `uv.lock`, `package.json`, `pnpm-lock.yaml`) from external contributors require a Discussion/Issue first (see `CONTRIBUTING.md`).

## Backend architecture

Each backend feature is a **module** under `backend/src/modules/<name>/` (`auth`, `users`, `friends`, `servers`, `channels`, `chats`, `messages`). All 7 modules follow the same layered, CQRS/mediator layout:

```
modules/<name>/
  domain/
    entities/          rich domain objects (plain classes subclassing shared.domain.Entity/
                        AggregateRoot — not Pydantic), one per file (e.g. `user.py`, `server.py`)
    entities/dtos.py   plain `@dataclass(frozen=True, kw_only=True)` DTOs: persistence create/
                        update payloads, read-model/query-result DTOs, facade DTOs (e.g.
                        `UserDTO`, `ChannelDTO`). Never Pydantic — see "Pydantic is transport-only"
                        below.
    repository Protocols, unit-of-work ABC, exceptions (LumiereError subclasses), enums
  application/
    commands/          one <Name>Command (frozen kw-only dataclass, data-only) + a separate
                        <Name>CommandHandler class with `async def handle(command) -> Result[T, E]`
    queries/            same shape: <Name>Query dataclass + <Name>QueryHandler
  infrastructure/
    persistence/        SQLAlchemy ORM models, repository implementations, model<->entity mappers
    <name>_unit_of_work_impl.py   concrete UnitOfWork wiring repositories to one AsyncSession
  public/
    facade.py            the module's boundary for OTHER modules: a `<Name>Facade` Protocol
                        (structurally typed, so consumers can fake it in unit tests without
                        building a real mediator/DB) plus a concrete impl and a
                        `build_<name>_facade(session[, stack])` factory. Present on modules that
                        at least one other module depends on (`users`, `channels`, `chats`,
                        `servers`); modules nothing else depends on (`auth`, `friends`,
                        `messages`) have no `public/` package. Other modules import ONLY from
                        here — never another module's `domain/`/`application/`/`infrastructure/`.
  transport/http/
    router.py           FastAPI APIRouter; takes MediatorDep, builds a Command/Query, calls
                        `mediator.send(...)`/`mediator.query(...)`, unwraps the Result
    dependencies.py      only what's still needed directly: non-command, module-owned transport
                        concerns (e.g. auth's cookie extraction). Cross-cutting deps used by
                        several modules (e.g. `UserIdDep`/JWT->user-id decoding) live in
                        `api/v1/dependencies.py` instead, not in any one module. Several modules
                        have no dependencies.py at all — deleted once nothing outside the module
                        needed it.
  composition.py        register_<name>_handlers(registry: HandlerRegistry) — registers one
                        factory closure per command/query on the process-lifetime HandlerRegistry
                        (`shared/application/handler_registry.py`). A factory takes
                        `(services: RequestServices, mediator: Mediator)` and is called lazily, at
                        dispatch time, to build just the one handler (and its UoW/repositories)
                        a request actually needs — it constructs these from `services.session`
                        itself, never from anything captured at registration time. Called ONCE,
                        at app startup, from `composition/handlers.py::build_handler_registry()`
                        — not from `composition/container.py` (that file only handles HTTP router
                        mounting) and not per-request. Also where a factory builds *other*
                        modules' facades it needs (e.g. `auth`'s login/register factories build
                        `MediatorUsersFacade(mediator)` inline, using the mediator instance passed
                        in at dispatch time — this has no ordering hazard since a factory never
                        runs before the mediator dispatching it is fully constructed).
  module.py            register_<name>_module() -> APIRouter, called from composition/container.py
```

Key conventions:
- **Domain layer has zero framework/ORM dependencies.** Repository and UnitOfWork contracts are `Protocol`/ABC classes in `domain/repositories/`; only `infrastructure/` imports SQLAlchemy.
- **Pydantic is transport-only.** `BaseSchema`/`BaseModel` appear *only* in `transport/http/schemas.py` (HTTP request bodies and response models) or, for trivial inline cases, `transport/http/router.py`. Everywhere else — `domain/`, `application/`, `public/` — is plain Python: rich `Entity`/`AggregateRoot` subclasses, or `@dataclass(frozen=True, kw_only=True)` DTOs in `domain/entities/dtos.py`. This includes Command/Query fields (never a Pydantic object — see below), facade return types (`UserDTO`, `ChannelDTO`, …), and persistence create/update payloads. A transport `*Request` class and its domain-side dataclass mirror commonly share the same field set (e.g. `ServerCreateRequest` / `ServerCreateData`) — the router converts one to the other explicitly (`SomeData(**request.model_dump())` for full payloads; see the partial-update bullet below for updates).
- **Entities are rich objects.** Anything with identity that a command mutates (`Chat`, `Server`, `User`, `Message`, …) subclasses `shared/domain/entity.py::Entity` or `aggregate_root.py::AggregateRoot` (only where domain events matter — most entities are plain `Entity`; only `Chat` currently records one, `ChatCreatedEvent`, purely to prove the plumbing, not as a general event-bus pattern). Where a router used to return an entity (or a domain dataclass DTO) directly as `response_model`, it bridges through a dedicated `*Response` DTO via `SomeResponse.model_validate(value)` — this works via `from_attributes=True` regardless of whether `value` is an `Entity` or a plain dataclass, including recursively through `list[...]` fields and `Discriminator`-based unions (see `chats.transport.http.schemas.ChatSummaryPageResponse` / `messages.transport.http.schemas.MessageResponse` for discriminated-union examples).
- **Partial updates use an `Unsettable`/`UNSET` sentinel, not `None`.** `shared/domain/unset.py` defines `UNSET` (a singleton sentinel) and `Unsettable[T] = T | _UnsetType`; a domain Update dataclass types its optional fields `Unsettable[str] = UNSET` etc. `shared/domain/unset.py::set_fields(data)` returns only the fields that aren't `UNSET`, replacing Pydantic's `model_dump(exclude_unset=True)` in repository `update()` methods (which therefore no longer take an `exclude_unset` bool param — it's implicit). On the write path, `shared/schemas/bridge.py::unsettable_from_request(request, DataclassType)` builds the dataclass from a Pydantic request using `request.model_fields_set` to decide which fields the client actually sent vs. leave `UNSET`.
- **Commands/queries are dispatched through the mediator, not injected directly.** `api/v1/dependencies.py::get_mediator` builds a fresh `InProcessMediator` per request — a request-scoped `RequestServices` (session/event_bus/cache/realtime_notifier) plus a reference to the process-lifetime `HandlerRegistry` on `app.state.handler_registry` — so a fresh mediator instance is still needed per request for session isolation, even though every module's handler *factories* are registered only once, at startup, not per request. Routers depend on `MediatorDep` and call `mediator.send(SomeCommand(...))` / `mediator.query(SomeQuery(...))`; the mediator resolves the command/query type's registered factory and calls it with `(services, self)` to build the one handler needed. `shared/application/mediator.py`'s `Mediator` Protocol is what domain/application/transport code depends on; `shared/application/in_process_mediator.py::InProcessMediator` is the only implementation. See the DI lifetime model below for the full singleton/request-scoped/per-dispatch breakdown.
- **Commands/queries are frozen, kw-only dataclasses** carrying primitive data only (`shared/application/command.py`, `query.py`) — no ORM models or domain entities crossing that boundary. The actual logic lives in a separate `<Name>CommandHandler`/`<Name>QueryHandler` class with a `handle()` method.
- **Expected business failures return `Result[T, LumiereError]`** (`shared/result.py`), not a raised exception — `Result.err(SomeLumiereError())` / `Result.ok(value)`. Routers unwrap with `if result.is_err: raise result.error` (the error value is already a real `LumiereError` instance, so `api/errors.py`'s existing handler catches it unchanged). Reserve actual `raise` for genuinely unexpected/programmer errors. When a command delegates to another module's facade method that itself raises (e.g. `chats.public.facade.ChatsFacade.assert_is_chat_member`, `servers.public.facade.ServersFacade.assert_is_server_member`), catch the raise at the command's own boundary and convert it — either a specific `except SomeError:` or, when several distinct `LumiereError` subclasses can surface from delegated calls, a broader `except LumiereError as error: return Result.err(error)`.
- **Modules do not import each other's `domain/`/`application/`/`infrastructure/`.** Cross-module access goes through the target module's `public/facade.py` (a `<Name>Facade` Protocol + concrete impl + `build_<name>_facade(...)` factory), returning DTOs (e.g. `UserDTO`, `ChannelDTO`) or raising the target module's own domain exceptions — never an entity or ORM model. This is what makes a module extractable later: swap the facade's implementation for an RPC/HTTP client and nothing else changes. `shared/` itself must stay module-agnostic too — cross-module permission-check helpers that used to live in `shared/permissions/{chat,server}.py` were moved into `modules/{chats,servers}/domain/services.py`, exposed only via those modules' facades.
- Routers stay thin: build the Command/Query, dispatch via the mediator, unwrap the Result, return — business logic belongs in the handler.
- Mappers (`infrastructure/persistence/mappers.py`) are the only place ORM rows/models get converted to domain entities; repositories never leak ORM objects upward.
- Unit of Work (`shared/data/unit_of_work/BaseUnitOfWork`) wraps a request's `AsyncSession` and exposes module repositories as attributes (e.g. `uow.chats`, `uow.members`); handlers call `uow.commit()` explicitly after mutating through repositories. A `BaseUnitOfWork` is a plain attribute holder, not a context manager — it owns none of the session's lifecycle (no close, no rollback-on-exception), since one physical session is shared across several per-module `UnitOfWork` instances constructed over the course of a single request (each module's own factory in its `composition.py` builds its own, from `RequestServices.session`). Session close and exception-triggered rollback are owned solely by the request-scoped `get_session` dependency (`core/database/session.py`, wired in `api/v1/dependencies.py`).
- Cross-module reads sometimes reach directly into another module's ORM models (e.g. `chats` repository joins `messages` and `users` ORM models) rather than going through that module's repository — this is an accepted shortcut for read-heavy queries, not a pattern to generalize into write paths. A command that needs another module's *write* behavior as part of its own atomic operation (e.g. `servers.CreateServerCommandHandler` creating a server's default channel, `messages.SendChatMessageCommandHandler` incrementing a chat's sequence counter) still holds a same-session repository/handler instance built by its own `composition.py` — via the producer module's facade where one exists (`ChannelsFacade.create_default_channel`), or a directly-composed repository where the write is cheap/narrow enough not to need one (`MessageUnitOfWork.chats`/`.channels`) — not a mediator dispatch, since the mediator is for HTTP-triggered dispatch, not inter-command calls, and a mediator round-trip wouldn't share the caller's uncommitted transaction.
- App-level errors subclass `LumiereError` (`shared/errors/base.py`; `NotFoundError`, `ConflictError`, `ValidationError`), each with a default `detail`/`status_code`. Register new domain-specific errors as subclasses in the module's `domain/exceptions.py`; the global handler in `api/errors.py` converts any `LumiereError` to a JSON `{"detail": ...}` response automatically.
- `composition/container.py` is the place new modules get their HTTP router registered (`register_<name>_module()` appended to `Container.module_routers`); `api/v1/router.py` mounts all of them under `/api/v1`. This is unrelated to the mediator/handler wiring: `composition/handlers.py::build_handler_registry()` is where every module's `register_<name>_handlers(registry)` gets called, once, at startup — both are invoked from `main.py::create_app()`, stored on `app.state.container`/`app.state.handler_registry` respectively. A module needs a `module.py` (router mounting), a `composition.py` (handler factory registration), *and* an entry in each of `container.py`/`handlers.py` to actually be wired up.
- Settings (`core/config/settings.py`) are a single `pydantic-settings` `Settings` object reading `../.env`; add new env vars there, not via `os.environ` reads.
- Linting is strict: `mypy --strict` (backend `pyproject.toml`), ruff with `ARG001` (no unused args) and `T201` (no `print`) enabled. `mypy` isn't run on `tests/` by `scripts/lint.sh`, but keeping it clean there too is worth doing. For the remaining Pydantic request/response models in `transport/http/`, strict mode without the pydantic mypy plugin means constructing one with only some fields set requires either supplying every field or a `# type: ignore[call-arg]`; prefer the latter for optional fields you want to leave genuinely unset.
- Unit tests (`tests/unit/<module>/`) construct handlers directly with hand-written in-memory fakes for that module's repository Protocols and any facade Protocols it depends on (colocated as `tests/unit/<module>/fakes.py`, not centralized) — no DB, no HTTP, no app instance. Where a module's UnitOfWork is an ABC rather than a Protocol, its fake must explicitly subclass it (structural typing alone won't satisfy mypy for a concrete base class). A module whose UnitOfWork still composes another module's repository directly for a same-transaction write (e.g. `messages`' `chats`/`channels` repos, needed for `increment_sequence`) reuses that other module's already-built fakes rather than duplicating them; a `Fake<Name>Facade` (e.g. `FakeChatsFacade`, `FakeUsersFacade`) is likewise colocated in the producer module's own `tests/unit/<module>/fakes.py` and imported by consumers.

### DI lifetime model

Three lifetimes, all built explicitly (FastAPI's native `Depends()` plus `app.state` — no third-party DI container, no contextvar-based implicit session):

- **Singleton / process lifetime** — built once in `main.py`'s `lifespan()`/`create_app()`, stored on `app.state`: the DB engine and sessionmaker (`app.state.db_engine`/`.session_factory`, disposed on shutdown alongside Redis), the Redis client (`app.state.redis`), the read-model cache and event bus (`app.state.cache`/`.event_bus`), the router `Container` (`app.state.container`), the `HandlerRegistry` (`app.state.handler_registry`, built by `composition/handlers.py::build_handler_registry()`), and `Settings`. None of these are per-request work, and none use `@lru_cache`-decorated module functions as a substitute for this — that pattern was replaced (the DB engine/sessionmaker used to be `@lru_cache`d in `core/database/session.py`, with no disposal hook, before being moved here for consistency with everything else).
- **Request-scoped** — one per HTTP request, torn down when it ends: the `AsyncSession` (`SessionDep` → `get_session`, which is the sole owner of session close and exception-triggered rollback), and the `RequestServices` bundle (`shared/application/handler_registry.py`: that session plus the event_bus/cache/realtime_notifier references) that `get_mediator` builds and hands to a fresh `InProcessMediator` every request. A fresh mediator per request is still required even though handler *factories* are process-lifetime — session isolation lives in `RequestServices`, not in the registry.
- **Per-dispatch** — built lazily, only when actually needed: the one handler (and its UoW/repositories, and any facades it needs) that a specific `mediator.send()`/`.query()` call resolves via the `HandlerRegistry`. A request that dispatches one command touches exactly one handler's worth of repositories/UoW, not all ~40+ handlers across all 7 modules — this is what "register handlers once" means in practice: the *mapping* of command/query type → factory is singleton, but every construction it triggers is still fresh per dispatch, scoped to that request's own session.

## Frontend architecture

Feature-sliced structure under `frontend/src/`:

```
entities/    domain types only (server, user) — no API calls, no UI
features/    self-contained feature modules, each with api/ model/ ui/
pages/       page components composing features
routes/      TanStack Router file-based route definitions (routeTree.gen.ts is generated, do not edit)
shared/
  api/       axios instance with auth-refresh interceptor
  config/    env vars (src/shared/config/env.ts)
  helpers/   utilities (cn, timeAgo, auth)
  ui/        shadcn/ui primitives (Radix + data-slot pattern)
```

- State: server state via TanStack Query hooks in `features/*/model/`; client state via Zustand where needed.
- Styling: Tailwind v4 exclusively; merge classes with the `cn()` helper (`clsx` + `tailwind-merge`), never build one-off class strings.
- `src/client` (generated OpenAPI SDK) is excluded from end-of-file/whitespace pre-commit hooks and typo checks — don't hand-edit it, regenerate via `scripts/generate-client.sh` instead.
- Design system reference: `frontend/UI.md` — semantic CSS custom properties (`--color-*`, `--font-*`, spacing/radius scale), dark-first with a `[data-theme='light']` override. Use the documented tokens, not raw hex values, in any new component.

### Import ordering (enforced by Prettier + `@ianvs/prettier-plugin-sort-imports`, run `pnpm run format` to fix)

Grouped with blank lines in this order: `react` → third-party packages → `@/shared/*` → `@/entities/*` → `@/features/*`/`@/pages/*` → relative (`./`, `../`). Use `import type { ... }` for type-only imports; prefer the `@/` alias over deep relative paths across modules.

### Doc comments

Use `/** ... */` JSDoc blocks (1–3 lines, document *why* not *what*) above every public function, component, and hook — the TS equivalent of the backend's docstring-light style. Skip `@param`/`@returns` unless the signature is unclear.

## Claude Code project tooling

These entries are specific to Claude Code; agents that don't read `.claude/` can skip this section.

`.claude/agents/` — read-only reviewer subagents grounded in this file's conventions (not generic textbook patterns):
- `backend-architecture-reviewer` — reviews `backend/src/` changes against the "Backend architecture" conventions above (facade-only cross-module access, `Result` vs raise, CQRS/mediator wiring, `Unsettable`/`UNSET`, etc.), using `channels`/`chats` as reference modules.
- `frontend-architecture-reviewer` — reviews `frontend/src/` changes against the "Frontend architecture" conventions below (feature-sliced layering, `cn()`/Tailwind tokens per `frontend/UI.md`, import ordering).

`.claude/skills/` — project-specific skills:
- `new-backend-module` — step-by-step scaffold for a new `backend/src/modules/<name>/` module following the layout above, in dependency order (domain → infrastructure → application → facade → transport → wiring → tests).
- `backend-verify` — backend done-checklist: `scripts/lint.sh` + `scripts/test.sh`.
- `frontend-verify` — frontend done-checklist: `lint`, `format:check`, `test`, `build`.

## Cross-cutting notes

- The frontend API client (`frontend/src/client`, `frontend/openapi.json`) is generated from the backend's live OpenAPI schema — backend route/schema changes are the source of truth, not the other way around.
- `pnpm-workspace.yaml` + root `package.json` wrap the single `frontend` package; there's no other JS workspace member yet.
- `backend/pyproject.toml` is a `uv` workspace with `backend` as its only member (`[tool.uv.workspace]` in root `pyproject.toml`).
