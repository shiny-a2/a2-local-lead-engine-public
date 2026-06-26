# 10 - Go / No-Go For Dry-Run

## Verdict

**NO_GO_ENV_DB_BLOCKED**

## Reason

The project is code-ready for operator setup, but controlled dry-run cannot start because:

- `.env` is missing.
- DB connectivity failed with `OperationalError`.
- migrations have not been checked against a reachable DB.
- dashboard auth username/password hash are missing.

## Allowed Next Step

Operator DB/env setup only.

## Not Allowed Yet

- live source/API collection
- OpenAI calls
- SMTP/email sending
- inbox sync
- lead collection
- disabling kill switch

## Exact Next Command After Manual Setup

After `.env` and DB are configured:

```powershell
uv run python -m app.cli.main doctor
```

If database is ok, continue with:

```powershell
uv run alembic current
uv run alembic upgrade head
uv run python -m app.cli.main safety check
uv run python -m app.cli.main ops readiness --campaign auckland-local-website-pilot
```
