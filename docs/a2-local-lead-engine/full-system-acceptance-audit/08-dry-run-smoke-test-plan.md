# 08 - Dry-Run Smoke Test Plan

Do not run live sends or live source/API calls. Start only after database and `.env` are configured for a local/private environment.

| Step | Command | Expected safe output | Required env/data | Amirali must provide first? |
|---:|---|---|---|---:|
| 1 | `uv run python -m app.cli.main doctor` | DB ok, risky operations disabled | DB URL | Yes |
| 2 | `uv run python -m app.cli.main config check` | Redacted config, no secrets exposed | `.env` | Yes |
| 3 | `uv run python -m app.cli.main safety check` | Risky operations blocked unless intentionally enabled for specific dry-run phase | `.env` | Yes |
| 4 | `uv run python -m app.cli.main campaign seed` | Campaign exists | DB | Yes |
| 5 | `uv run python -m app.cli.main sources check` | Connector readiness, no network call | source keys optional | No |
| 6 | `uv run python -m app.cli.main collect geoapify --campaign auckland-local-website-pilot --city Auckland --country "New Zealand" --category barber --limit 3 --dry-run` | Source run dry plan/report; no external API call | campaign/DB | Yes |
| 7 | `uv run python -m app.cli.main normalize run --campaign auckland-local-website-pilot --all-raw --limit 3 --dry-run` | Candidate dry-run report | raw records if any | Maybe |
| 8 | `uv run python -m app.cli.main verify plan --campaign auckland-local-website-pilot --limit 3 --dry-run` | Verification plan only | candidates | Maybe |
| 9 | `uv run python -m app.cli.main score candidates --campaign auckland-local-website-pilot --limit 3 --dry-run` | Score dry-run report | verified candidates | Maybe |
| 10 | `uv run python -m app.cli.main insight generate --campaign auckland-local-website-pilot --limit 3 --dry-run` | Insight dry-run | Phase 5 decisions | Maybe |
| 11 | `uv run python -m app.cli.main offer match --campaign auckland-local-website-pilot --limit 3 --dry-run` | Offer dry-run | Phase 6 data | Maybe |
| 12 | `uv run python -m app.cli.main email generate --campaign auckland-local-website-pilot --limit 3 --dry-run` | Prompt plan/safety status; no OpenAI | Phase 6 ready data | Yes |
| 13 | `uv run python -m app.cli.main judge emails --campaign auckland-local-website-pilot --dry-run` | Rule judge in-memory/dry result; no AI | draft variants | Yes |
| 14 | `uv run python -m app.cli.main review build-queue --campaign auckland-local-website-pilot --judge-run-id <run_id> --dry-run` | Eligible review queue plan | Phase 8 run id | Yes |
| 15 | `uv run python -m app.cli.main send build-queue --campaign auckland-local-website-pilot --human-review-run-id <run_id> --dry-run` | Send queue plan; no SMTP | Phase 9 run id | Yes |
| 16 | `uv run python -m app.cli.main send run --campaign auckland-local-website-pilot --limit 1 --dry-run` | Dry send plan; provider not called | send queue | Yes |
| 17 | `uv run python -m app.cli.main inbox plan --mailbox default` | Mailbox readiness and no import | IMAP settings optional | No |
| 18 | `uv run python -m app.cli.main inbox sync --mailbox default --dry-run` | No imports, no IMAP mutation | DB | Yes |
| 19 | `uv run python -m app.cli.main opportunity build --campaign auckland-local-website-pilot --dry-run` | Opportunity plan only | inbound classifications | Maybe |
| 20 | `uv run python -m app.cli.main sales-workspace build --campaign auckland-local-website-pilot --dry-run` | Workspace plan only | opportunities | Maybe |
| 21 | Phase 14 governance dry-run | Not available | N/A | BLOCK |
| 22 | Phase 15 country check dry-run | Not available | N/A | BLOCK |

## Stop Points

- `STOP_AND_REVIEW` after first source dry-run.
- `STOP_AND_REVIEW` after verification dry-run.
- `STOP_AND_REVIEW` after email drafts dry-run.
- `STOP_AND_REVIEW` before any send queue commit.
- `STOP_AND_REVIEW` before disabling kill switch or enabling provider send.
