---
name: backend-verify
description: Run the standard done-checklist for backend (backend/) changes — lint, tests, and frontend SDK regeneration. Use before considering any backend/src or backend/tests change complete.
---

# Backend verify

Run this after any change under `backend/`, before telling the user the work is done.

1. **Lint** (mypy strict + ruff check + ruff format check):
   ```bash
   cd backend && bash scripts/lint.sh
   ```
   If it fails on formatting/fixable ruff issues, run `bash scripts/format.sh` and re-run lint. Do not hand-fix what `ruff check --fix` / `ruff format` already fixes.

2. **Tests** (needs Postgres + Redis running — via `docker compose watch` or natively; requires `ENVIRONMENT=testing`, see `.env.test`):
   ```bash
   cd backend && bash scripts/test.sh
   ```
   To scope to what changed, prefer `uv run pytest tests/integration/<module> -k <name>` or `uv run pytest tests/unit` while iterating, then run the full `scripts/test.sh` once before declaring done.

Report which of these actually ran and their pass/fail — don't claim "done" from lint alone if the backend logic changed.
