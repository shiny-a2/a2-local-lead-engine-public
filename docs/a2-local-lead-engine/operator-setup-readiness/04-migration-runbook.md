# 04 - Migration Runbook

Do not run migrations against a production-like DB without a backup.

## Steps

1. Confirm the target DB is local/private.
2. Take a DB backup first.
3. Confirm `.env` exists and `DATABASE_URL` points to the intended DB.
4. Run:

```powershell
uv run alembic current
```

5. If the DB is reachable, run:

```powershell
uv run alembic upgrade head
```

6. Confirm head:

```powershell
uv run alembic current
```

7. Run doctor:

```powershell
uv run python -m app.cli.main doctor
```

8. Run ops readiness:

```powershell
uv run python -m app.cli.main ops readiness --campaign auckland-local-website-pilot
```

9. Stop and review the output.

## Stop Conditions

- DB connection error
- migration failure
- missing dashboard auth
- missing reports/export paths
- any safety flag unexpectedly enabled
- any secret printed in output
