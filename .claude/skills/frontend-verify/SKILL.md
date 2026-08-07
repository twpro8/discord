---
name: frontend-verify
description: Run the standard done-checklist for frontend (frontend/) changes — lint, formatting, tests, and production build. Use before considering any frontend/src change complete.
---

# Frontend verify

Run this after any change under `frontend/`, before telling the user the work is done. Run commands from `frontend/` unless a command says otherwise.

1. **Lint** (Oxlint):
   ```bash
   pnpm run lint
   ```

2. **Formatting** (Prettier also sorts imports):
   ```bash
   pnpm run format:check
   ```
   If it fails, run `pnpm run format`, inspect the resulting diff, and run the check again. Do not manually reproduce formatting changes that Prettier can make safely.

3. **Tests** (Vitest):
   ```bash
   pnpm run test
   ```
   While iterating, run the closest relevant test file first, then run the full suite before declaring frontend behavior complete.

4. **Production build** (TypeScript project build plus Vite):
   ```bash
   pnpm run build
   ```

5. **Generated API client** — only if the frontend depends on a backend route/schema change:
   ```bash
   cd .. && bash scripts/generate-client.sh
   ```
   Never hand-edit `src/client/`, `routeTree.gen.ts`, or `openapi.json` to make checks pass.

Report exactly which checks ran and their pass/fail state. A passing lint command alone is not sufficient evidence that changed frontend behavior is complete.
