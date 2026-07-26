# Lumiere Frontend

A real-time chat application frontend built with React 19, TanStack Router, and TanStack Query.

## Quick start

```bash
pnpm install
pnpm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/api` requests to the backend at `http://localhost:8000`.

For the full Docker-based development environment (backend + database + mailcatcher), see [development.md](../development.md) in the project root.

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm run dev` | Start Vite dev server with HMR |
| `pnpm run build` | Type-check and bundle for production |
| `pnpm run lint` | Run oxlint across the source |
| `pnpm run format` | Auto-format all source files with Prettier |
| `pnpm run format:check` | Check formatting without writing |
| `pnpm run preview` | Preview the production build locally |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

See `src/shared/config/env.ts` for where these are consumed.

## Architecture

```
src/
  entities/       Domain types only (server, user)
  features/       Feature modules, each with api/ model/ ui/
  pages/          Page components composing features
  routes/         TanStack Router route definitions
  shared/
    api/          Axios instance with auth refresh interceptor
    config/       Environment variables
    helpers/      Utility functions (cn, timeAgo, auth)
    ui/           Design system primitives (button, input, dialog, etc.)
```

- **Feature-sliced** — each feature is self-contained with its API calls, hooks, and UI components.
- **TanStack Router** — file-based routing in `routes/`, auto-generated `routeTree.gen.ts`.
- **TanStack Query** — server state via custom hooks in `features/*/model/`.
- **Tailwind v4** — all styling; `cn()` utility (`clsx` + `tailwind-merge`) for class merging.
- **shadcn/ui** — Radix UI primitives wrapped with the `data-slot` pattern.
- **Zustand** — client state where needed.

## Import conventions

Imports are organized into labelled groups separated by blank lines, enforced by Prettier + `@ianvs/prettier-plugin-sort-imports`. Run `pnpm run format` to auto-sort.

```
// react
import { useState } from "react"
import { createRoot } from "react-dom/client"

// third party
import { useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

// shared
import { api } from "@/shared/api/axios"
import { cn } from "@/shared/helpers/utils"

// entities
import type { Server } from "@/entities/server/model/types"

// features
import { useServers } from "@/features/servers/model/use-servers"
import HomePage from "@/pages/home/HomePage"

// relative
import { getMyServers } from "../api/get-servers"
import { AvatarInitial } from "./avatar-initial"
```

**Rules:**
- React and React DOM go in `// react`
- npm packages go in `// third party`
- `@/shared/*` aliases go in `// shared`
- `@/entities/*` aliases go in `// entities`
- `@/features/*` and `@/pages/*` aliases go in `// features`
- `./` and `../` relative imports go in `// relative`
- Use `import type { ... }` for type-only imports; inline `type` keyword when mixing values and types from the same module
- Prefer `@/` alias over deep relative `../../../` for cross-module imports

## Design

See [UI.md](UI.md) for the design system: tokens, typography, spacing, components, and accessibility.

## Docstring conventions

Use `/** ... */` JSDoc block comments above functions, components, hooks, and types — the equivalent of Python docstrings for TypeScript.

```ts
/** Returns the current user's server list. */
export function useServers() {
  return useQuery({ ... })
}

/** Renders a primary action button with optional icon. */
export function Button({ ... }: ButtonProps) {
  ...
}
```

Guidelines:
- Keep it short — 1-3 lines, document the *why* not the *what*
- Skip `@param` / `@returns` unless the signature alone is unclear
- Use `//` line comments only for implementation notes inside a function body
- Be consistent — every public function, hook, and component gets a block comment
