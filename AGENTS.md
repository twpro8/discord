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

Each backend feature is a **module** under `backend/src/modules/<name>/` (`auth`, `users`, `friends`, `servers`, `channels`, `chats`, `messages`). All 7 modules follow the same layered layout, with **use cases** as the application layer (no CQRS mediator/bus — that was ripped out in favor of native FastAPI dependency injection):

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
  usecases/
    one file per operation, each a `<Name>UseCase` class: dependencies (UoW, facades, ...) in
    `__init__`, the operation itself as `async def __call__(self, *, ...) -> T` taking plain
    keyword arguments — no wrapper Command/Query dataclass, no separate handler class. Returns
    the actual value and raises a `LumiereError` subclass on failure (see the raise-not-Result
    bullet below). A few modules also keep small private helpers here that only their own use
    cases share (e.g. `chats`/`servers`' `realtime.py` room-join helpers, `auth`'s
    `token_helper.py`) — these aren't use cases themselves, just glue.
  adapters/
    persistence/        SQLAlchemy ORM models, repository implementations, model<->entity mappers
    <name>_unit_of_work_impl.py   concrete UnitOfWork wiring repositories to one AsyncSession
  public/
    facade.py            the module's boundary for OTHER modules: a `<Name>Facade` Protocol
                        (structurally typed, so consumers can fake it in unit tests without
                        building a real DB) plus a concrete impl and a `build_<name>_facade(session)`
                        factory. Deliberately framework-free (no FastAPI import) — it's a plain
                        function (or, when the facade needs a UnitOfWork's commit/rollback
                        lifecycle, a plain async generator yielding the facade once inside
                        `async with SomeUnitOfWorkImpl(...) as uow:`). Present on modules that at
                        least one other module depends on (`users`, `channels`, `chats`,
                        `servers`, `friends`); modules nothing else depends on (`auth`,
                        `messages`) have no `public/` package. Other modules import ONLY from
                        here — never another module's `domain/`/`usecases/`/`adapters/`.
  transport/http/
    router.py           FastAPI APIRouter; takes a `<Name>UseCaseDep`, calls `await use_case(...)`
                        with keyword arguments, and returns/validates the result directly — no
                        unwrapping, since a raised `LumiereError` propagates straight to
                        `api/errors.py`'s global exception handler on its own.
    dependencies.py      per-module FastAPI DI wiring: a UnitOfWork provider (an async-generator
                        `async def get_<name>_unit_of_work(session: SessionDep) -> AsyncGenerator[XUnitOfWork]`
                        doing `async with XUnitOfWorkImpl(...) as uow: yield uow`), a provider +
                        `Annotated[X, Depends(get_x)]` Dep alias per use case, and — for every
                        other module's facade this one needs — a small locally-defined wrapper
                        (`async def get_x_facade(session: SessionDep) -> XFacade: return
                        build_x_facade(session)`, or `contextlib.aclosing`-wrapped if the
                        producer's factory is itself an async generator) built only from that
                        producer's `public/facade.py`, never its `transport/`. All provider
                        functions come first, then every `...Dep = Annotated[...]` alias
                        together at the end of the file. Also holds non-use-case, module-owned
                        transport concerns (e.g. auth's cookie extraction). Cross-cutting deps
                        used by several modules (`UserIdDep`, `SessionDep`, `RealtimeNotifierDep`,
                        `RoomMembershipUpdaterDep`, ...) live in `api/v1/dependencies.py` instead,
                        imported from there rather than redefined per module.
  module.py            register_<name>_module() -> APIRouter, called from composition/container.py
```

Key conventions:
- **Domain layer has zero framework/ORM dependencies.** Repository and UnitOfWork contracts are `Protocol`/ABC classes in `domain/repositories/`; only `adapters/` imports SQLAlchemy.
- **Pydantic is transport-only.** `BaseSchema`/`BaseModel` appear *only* in `transport/http/schemas.py` (HTTP request bodies and response models) or, for trivial inline cases, `transport/http/router.py`. Everywhere else — `domain/`, `usecases/`, `public/` — is plain Python: rich `Entity`/`AggregateRoot` subclasses, or `@dataclass(frozen=True, kw_only=True)` DTOs in `domain/entities/dtos.py`. This includes a use case's `__call__` parameters (plain keyword args, never a Pydantic object), facade return types (`UserDTO`, `ChannelDTO`, …), and persistence create/update payloads. A transport `*Request` class and its domain-side dataclass mirror commonly share the same field set (e.g. `ServerCreateRequest` / `ServerCreateData`) — the router converts one to the other explicitly (`SomeData(**request.model_dump())` for full payloads; see the partial-update bullet below for updates).
- **Entities are rich objects.** Anything with identity that a use case mutates (`Chat`, `Server`, `User`, `Message`, …) subclasses `shared/domain/entity.py::Entity` or `aggregate_root.py::AggregateRoot` (only where domain events matter — most entities are plain `Entity`; only `Chat` currently records one, `ChatCreatedEvent`, purely to prove the plumbing, not as a general event-bus pattern). Where a router used to return an entity (or a domain dataclass DTO) directly as `response_model`, it bridges through a dedicated `*Response` DTO via `SomeResponse.model_validate(value)` — this works via `from_attributes=True` regardless of whether `value` is an `Entity` or a plain dataclass, including recursively through `list[...]` fields and `Discriminator`-based unions (see `chats.transport.http.schemas.ChatSummaryPageResponse` / `messages.transport.http.schemas.MessageResponse` for discriminated-union examples).
- **Partial updates use an `Unsettable`/`UNSET` sentinel, not `None`.** `shared/domain/unset.py` defines `UNSET` (a singleton sentinel) and `Unsettable[T] = T | _UnsetType`; a domain Update dataclass types its optional fields `Unsettable[str] = UNSET` etc. `shared/domain/unset.py::set_fields(data)` returns only the fields that aren't `UNSET`, replacing Pydantic's `model_dump(exclude_unset=True)` in repository `update()` methods (which therefore no longer take an `exclude_unset` bool param — it's implicit). On the write path, `shared/schemas/bridge.py::unsettable_from_request(request, DataclassType)` builds the dataclass from a Pydantic request using `request.model_fields_set` to decide which fields the client actually sent vs. leave `UNSET`.
- **Use cases are injected directly via FastAPI's native DI, not dispatched through a bus.** Each module's `transport/http/dependencies.py` defines a `Depends()` provider + `Annotated[...] = Depends(...)` `<Name>UseCaseDep` alias per use case (see the module layout above); routers just declare the use case as a parameter and call it. This is deliberately lazier and cheaper than the old mediator setup: FastAPI only builds the specific use case (and its specific UoW/facade dependencies) an endpoint actually needs, instead of eagerly wiring every module's handlers on every request.
- **A use case is a single class with `__call__`**, not a Command/Query dataclass plus a separate Handler class — `CreateChannelUseCase(uow, servers_facade)` then `await use_case(channel_id=..., name=...)`. Constructor takes its collaborators (UoW, facades, cross-cutting services); `__call__` takes the operation's actual keyword arguments and returns the result value directly (or `None`).
- **Expected business failures `raise` a `LumiereError` subclass directly** — `raise SomeLumiereError` (or `raise SomeLumiereError(...)` with args) — not a `Result` wrapper. `LumiereError` already subclasses `Exception`, and `api/errors.py`'s global `@app.exception_handler(LumiereError)` already converts any raised instance to the right JSON/status-code response, so routers need no unwrapping at all: `channel = await use_case(...); return ChannelResponse.model_validate(channel)`. When a use case delegates to another module's facade method that itself raises (e.g. `chats.public.facade.ChatsFacade.assert_is_chat_member`, `servers.public.facade.ServersFacade.assert_is_server_member`), just let it propagate — there's no boundary conversion to do. Only wrap in `try/except` when the use case has real follow-up logic to run on that specific failure (e.g. `messages.DeleteMessageUseCase` probing ownership via a facade call and treating a denial as "not owner" rather than re-raising, or `auth.LoginUseCase` logging — not failing — on a best-effort notification email's error).
- **Modules do not import each other's `domain/`/`usecases/`/`adapters/`.** Cross-module access goes through the target module's `public/facade.py` (a `<Name>Facade` Protocol + concrete impl + `build_<name>_facade(...)` factory), returning DTOs (e.g. `UserDTO`, `ChannelDTO`) or raising the target module's own domain exceptions — never an entity or ORM model. This is what makes a module extractable later: swap the facade's implementation for an RPC/HTTP client and nothing else changes. The one narrow, deliberate exception is DI wiring at the transport layer: a router that needs another module's use case directly for a genuinely cross-module HTTP-triggered operation (e.g. `messages`' `list_chat_messages` endpoint importing `chats`' `MarkChatAsReadUseCaseDep` to auto-advance the read cursor after listing) imports that Dep alias from the producer's `transport/http/dependencies.py` — this is the direct replacement for what dispatching an arbitrary module's command through the old mediator used to allow. `shared/` itself must stay module-agnostic too — cross-module permission-check helpers that used to live in `shared/permissions/{chat,server}.py` were moved into `modules/{chats,servers}/domain/services.py`, exposed only via those modules' facades.
- Routers stay thin: call the use case with keyword arguments, return/validate the result — business logic belongs in the use case.
- Mappers (`adapters/persistence/mappers.py`) are the only place ORM rows/models get converted to domain entities; repositories never leak ORM objects upward.
- Unit of Work (`shared/data/unit_of_work/BaseUnitOfWork`) wraps one `AsyncSession` per request and exposes module repositories as attributes (e.g. `uow.chats`, `uow.members`); use cases call `uow.commit()` explicitly after mutating through repositories. Its `__aexit__` always closes the underlying session (rolling back first on an exception) — since several independent UoW instances can wrap the *same* shared request-scoped session within one request (one per use case actually used, torn down as FastAPI's dependency exit stack unwinds), closing an already-closed `AsyncSession` is relied upon to be a safe no-op.
- Cross-module reads sometimes reach directly into another module's ORM models (e.g. `chats` repository joins `messages` and `users` ORM models) rather than going through that module's repository — this is an accepted shortcut for read-heavy queries, not a pattern to generalize into write paths. A use case that needs another module's *write* behavior as part of its own atomic operation (e.g. `servers.CreateServerUseCase` creating a server's default channel, `messages.SendChatMessageUseCase` incrementing a chat's sequence counter) still holds a same-session repository/use-case instance built by its own `transport/http/dependencies.py` — via the producer module's facade where one exists (`ChannelsFacade.create_default_channel`), or a directly-composed repository where the write is cheap/narrow enough not to need one (`MessageUnitOfWork.chats`/`.channels`) — never a second, independent session/transaction, since that wouldn't share the caller's uncommitted work.
- App-level errors subclass `LumiereError` (`shared/errors/base.py`; `NotFoundError`, `ConflictError`, `ValidationError`), each with a default `detail`/`status_code`. Register new domain-specific errors as subclasses in the module's `domain/exceptions.py`; the global handler in `api/errors.py` converts any `LumiereError` to a JSON `{"detail": ...}` response automatically.
- `composition/container.py` is the place new modules get their HTTP router registered (`register_<name>_module()` appended to `Container.module_routers`); `api/v1/router.py` mounts all of them under `/api/v1`. A module needs just a `module.py` (router mounting) — there's no per-module wiring-registration file anymore (the old `composition.py`/mediator-registration step is gone; each module's own `transport/http/dependencies.py` is self-contained).
- Settings (`core/config/settings.py`) are a single `pydantic-settings` `Settings` object reading `../.env`; add new env vars there, not via `os.environ` reads.
- Linting is strict: `mypy --strict` (backend `pyproject.toml`), ruff with `ARG001` (no unused args) and `T201` (no `print`) enabled. `mypy` isn't run on `tests/` by `scripts/lint.sh`, but keeping it clean there too is worth doing. For the remaining Pydantic request/response models in `transport/http/`, strict mode without the pydantic mypy plugin means constructing one with only some fields set requires either supplying every field or a `# type: ignore[call-arg]`; prefer the latter for optional fields you want to leave genuinely unset.
- Unit tests (`tests/unit/<module>/`) construct use cases directly with hand-written in-memory fakes for that module's repository Protocols and any facade Protocols it depends on (colocated as `tests/unit/<module>/fakes.py`, not centralized) — no DB, no HTTP, no app instance. Call the use case with keyword arguments (`await use_case(chat_id=..., user_id=...)`) and assert on the returned value, or wrap the call in `pytest.raises(SomeLumiereError)` for failure cases — no `Result`/`.is_ok` assertions. Where a module's UnitOfWork is an ABC rather than a Protocol, its fake must explicitly subclass it (structural typing alone won't satisfy mypy for a concrete base class). A module whose UnitOfWork still composes another module's repository directly for a same-transaction write (e.g. `messages`' `chats`/`channels` repos, needed for `increment_sequence`) reuses that other module's already-built fakes rather than duplicating them; a `Fake<Name>Facade` (e.g. `FakeChatsFacade`, `FakeUsersFacade`) is likewise colocated in the producer module's own `tests/unit/<module>/fakes.py` and imported by consumers.

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
- `backend-architecture-reviewer` — reviews `backend/src/` changes against the "Backend architecture" conventions above (facade-only cross-module access, raise-not-Result error handling, use-case/native-DI wiring, `Unsettable`/`UNSET`, etc.), using `channels`/`chats` as reference modules.
- `frontend-architecture-reviewer` — reviews `frontend/src/` changes against the "Frontend architecture" conventions below (feature-sliced layering, `cn()`/Tailwind tokens per `frontend/UI.md`, import ordering).

`.claude/skills/` — project-specific skills:
- `new-backend-module` — step-by-step scaffold for a new `backend/src/modules/<name>/` module following the layout above, in dependency order (domain → adapters → application → facade → transport → wiring → tests).
- `backend-verify` — backend done-checklist: `scripts/lint.sh` + `scripts/test.sh`.
- `frontend-verify` — frontend done-checklist: `lint`, `format:check`, `test`, `build`.

## Cross-cutting notes

- The frontend API client (`frontend/src/client`, `frontend/openapi.json`) is generated from the backend's live OpenAPI schema — backend route/schema changes are the source of truth, not the other way around.
- `pnpm-workspace.yaml` + root `package.json` wrap the single `frontend` package; there's no other JS workspace member yet.
- `backend/pyproject.toml` is a `uv` workspace with `backend` as its only member (`[tool.uv.workspace]` in root `pyproject.toml`).
