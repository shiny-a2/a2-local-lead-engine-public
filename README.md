# A2 Local Lead Intelligence & Email Outreach Engine

A safety-first, 15-phase pipeline that finds local businesses **without a website** and
prepares honest, human-reviewed cold-outreach emails for them. It runs end to end on
**free, keyless** systems (no credit card), with email sending firmly gated behind a global
kill switch and a human-approval queue.

> Built for Amirali Yaghouti (simple websites for local businesses). Outreach sending stays
> OFF by default — the engine only produces a dry-run plan until a human deliberately enables it.

## Pipeline

```
collect (OpenStreetMap) → normalize → dedupe → quality → verify web presence (URL probe)
→ score → insight/offer → email draft → judge → human review → controlled send (dry-run)
→ inbox/reply → opportunity → sales workspace → pilot governance
```

## Free, keyless by default

| Stage | System | Cost |
|---|---|---|
| Lead collection | OpenStreetMap Overpass | free, no key, no card |
| Web verification | direct URL probe | free, no key |
| Email drafting | local template writer (or OpenAI if a key is set) | free / optional paid |
| Email judging | deterministic rule judge | free, no key |
| Database | local SQLite | free |
| Deliverability check | DNS-over-HTTPS (SPF/DKIM/DMARC) | free, no key |

The only optional paid service is the OpenAI (GPT) API; without it the engine drafts emails
locally for free. See `docs/free-keyless-run.md`.

## Quick start

```bash
uv sync --all-extras
cp .env.example .env          # set DATABASE_URL=sqlite:///./a2_local.db
uv run python -m alembic upgrade head

# run the whole free pipeline (live OSM → human-review queue; nothing is sent)
bash scripts/run_local_pipeline.sh Auckland beauty_salon 60

# countries & cities (12 countries, ~180 cities in app/config/geography.yaml)
uv run python -m app.cli.main geo countries
bash scripts/run_country_pipeline.sh "Australia" big beauty_salon 25
```

## Docs

- `docs/free-keyless-run.md` — how the free end-to-end run works + real results
- `docs/email-sending-setup.md` / `docs/cpanel-setup-fa.md` — sending from your own domain
- `docs/` — per-phase policies and the full-system acceptance audit

## Safety

`GLOBAL_OUTREACH_KILL_SWITCH=true`, sending/provider flags off, plain-text only, no tracking,
mandatory unsubscribe, suppression enforcement, and a human-approval gate before any send.
482+ tests, `ruff` clean.

## License

Private project; all rights reserved by the author.
