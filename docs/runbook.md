# Runbook

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Environment

Keep risky flags false in Phase 1. Config checks print `PRESENT` or `MISSING` for secrets and never show secret values.

## Database

Use PostgreSQL for normal local use:

```bash
python -m app.cli.main db upgrade
```

SQLite is acceptable for tests and isolated local fallback.

## Commands

```bash
python -m app.cli.main doctor
python -m app.cli.main config check
python -m app.cli.main campaign seed
python -m app.cli.main safety check
python -m app.cli.main fixtures seed
python -m app.cli.main report foundation
```

## Verify Safety

Run `safety check` and confirm live API calls, lead collection, AI generation, email drafting, email sending, followups, voice calls, Google Maps, and public dashboard are blocked.

## API

Bind only to localhost or a private network:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Do not expose the Phase 1 API publicly when `LOCAL_API_ONLY=true`.
