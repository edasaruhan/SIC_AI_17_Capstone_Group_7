# Local development

Requirements: Python 3.12 via uv; PostgreSQL 17 tools; Redis; Node 22 and pnpm 11.20.
All commands run from the official repository root.

```sh
uv sync --frozen
uv run python scripts/local_setup.py
uv run alembic upgrade head
uv run python scripts/migrate_test.py
uv run python scripts/local_redis.py
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

The setup creates an isolated PostgreSQL cluster under ignored `.local/postgres`
on port 55432, plus dedicated development/test databases and restricted roles.
It preserves existing `.env` and database state. Runtime passwords and the development
signing secret are generated locally into mode-600 `.env`, never committed.
The admin Unix socket is inside a mode-700 directory; network access uses SCRAM.
The runtime role cannot own tables, bypass RLS, or change schema. Run migrations
through the separate migration URL. Never use development auth in production.

Quality checks: `sh scripts/quality.sh`. Database integration tests require the
dedicated `growthpilot_test` database; migrations must be applied there first.
Infrastructure data, dependencies, local logs and generated previews are ignored.

Frontend: `pnpm install --frozen-lockfile`, `pnpm dev`; `pnpm typecheck`, `pnpm lint`,
`pnpm build`. Native install scripts are allowlisted only for esbuild/unrs-resolver.
The production build uses local/system fonts and requires no font CDN.

Redis uses a separate password-protected loopback instance on 56379 with private
state under `.local/redis`, not a system service. See `IMPORTS_AND_JOBS.md` for worker
and dispatcher commands. The runtime database and broker secrets stay in `.env`.
Integration tests use `growthpilot_test`, private temp objects, and a unique Redis
namespace; they must not be run against production.

CI is authored in `.github/workflows/quality.yml` with immutable action references,
locked dependencies and disposable services. GitHub-hosted execution cannot be
claimed until the final authorized publication; local equivalent gates are run now.
