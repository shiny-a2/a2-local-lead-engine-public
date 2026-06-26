# 08 - First Controlled Dry-Run Prerequisites

Controlled dry-run can start only after all items below pass:

- [ ] `.env` exists and is based on `.env.operator.example`.
- [ ] `DATABASE_URL` points to the intended local/private DB.
- [ ] `uv run python -m app.cli.main doctor` reports database ok.
- [ ] `uv run alembic current` works.
- [ ] `uv run alembic upgrade head` succeeds.
- [ ] Dashboard auth username and password hash are configured.
- [ ] `reports/`, `exports/`, and `logs/` are writable.
- [ ] `uv run python -m app.cli.main campaign seed` succeeds.
- [ ] `uv run python -m app.cli.main ops readiness --campaign auckland-local-website-pilot` has no unexpected blockers for dry-run.
- [ ] `uv run python -m app.cli.main pilot audit --campaign auckland-local-website-pilot --dry-run` works.
- [ ] Country/city/category selected: New Zealand / Auckland / first pilot category.
- [ ] All live/external/send flags remain false.
- [ ] `GLOBAL_OUTREACH_KILL_SWITCH=true`.

Live pilot remains blocked after this list; this is dry-run readiness only.
