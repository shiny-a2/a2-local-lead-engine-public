# Phase 1 Foundation

## Goal

Create a safe, local, offline foundation for A2 Local Lead Intelligence & Email Outreach Engine.

## In Scope

- Project skeleton
- Configuration and secret redaction
- SQLAlchemy models and Alembic migration
- Safety gates for risky operations
- Audit logs
- CLI commands
- Local/private FastAPI health and status endpoints
- Fake fixture data only
- Foundation readiness reports

## Out of Scope

- Real lead collection
- Live Geoapify, OSM/Overpass, Tavily, NZBN, OpenAI, SMTP, Google Maps, or Google Places calls
- AI email generation
- Email sending
- Voice calls
- Public dashboard

## Architecture

The CLI and API use shared settings, database models, services, and safety primitives. Sensitive operations must pass feature-flag checks before any future implementation can run.

## Safety Philosophy

Default mode is dry-run, local, offline, and non-sending. Dangerous work fails closed unless a later phase explicitly enables a reviewed feature flag.

## Commands

- `python -m app.cli.main doctor`
- `python -m app.cli.main config check`
- `python -m app.cli.main db upgrade`
- `python -m app.cli.main campaign seed`
- `python -m app.cli.main safety check`
- `python -m app.cli.main fixtures seed`
- `python -m app.cli.main report foundation`

## Acceptance Criteria

Tests pass, lint passes or has documented gaps, migrations create all tables, secrets are masked, risky operations are blocked by default, reports are generated, and no live external or sending paths exist.

