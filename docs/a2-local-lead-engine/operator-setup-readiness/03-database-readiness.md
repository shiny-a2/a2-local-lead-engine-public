# 03 - Database Readiness

## Findings

| Check | Result |
|---|---|
| `.env` file | Missing |
| `DATABASE_URL` key | Present in defaults/example |
| DB connectivity | Failed |
| Doctor verdict | `FOUNDATION_READY_WITH_GAPS` |
| Error class | `OperationalError` |
| Current migration version | Not checked because DB is unreachable |
| Pending migrations | Not checked because DB is unreachable |
| Tables present | Not checked because DB is unreachable |

## Migration Files Present

Migrations exist through Phase 14, including:

`alembic/versions/20260525_0014_phase14_pilot_governance.py`

## Blocker

The configured default DB URL is a placeholder and did not connect:

`postgresql+psycopg://user:***@localhost:5432/a2_leads`

## Exact Commands After DB Config

```powershell
uv run python -m app.cli.main doctor
uv run alembic current
uv run alembic upgrade head
uv run alembic current
uv run python -m app.cli.main doctor
```

Stop if any command fails.
