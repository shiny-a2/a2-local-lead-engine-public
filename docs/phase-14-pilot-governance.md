# Phase 14 - Pilot Governance, MVP Closure And Scale Gate

Phase 14 is a governance and reporting phase. It audits Phases 1-13, records KPI snapshots, risk register items, fix packs, ops readiness checks, retention policy, secret audit posture, and an MVP closure decision.

Phase 14 does not send emails, call SMTP, call OpenAI, call external source APIs, collect leads, sync inboxes, create follow-ups, generate proposals, quote prices, create payment links, schedule meetings, or place calls.

## Phase 15 Boundary

Phase 15 is post-MVP scale. For the tiny NZ/Auckland pilot, Phase 14 reports mark Phase 15 as `POST_MVP_SCALE_NOT_REQUIRED_FOR_NZ_TINY_PILOT`. This does not mean multi-country expansion is complete.

## CLI

- `python -m app.cli.main pilot audit --campaign auckland-local-website-pilot --dry-run`
- `python -m app.cli.main pilot audit --campaign auckland-local-website-pilot --commit`
- `python -m app.cli.main pilot report --run-id <pilot_audit_run_id>`
- `python -m app.cli.main pilot fixpacks --run-id <pilot_audit_run_id>`
- `python -m app.cli.main pilot scale-decision --run-id <pilot_audit_run_id>`
- `python -m app.cli.main ops readiness --campaign auckland-local-website-pilot`
- `python -m app.cli.main ops export --campaign auckland-local-website-pilot`

## Final Verdicts

- `MVP_CLOSED_READY`
- `MVP_CLOSED_WITH_FIX_PACKS`
- `MVP_NOT_CLOSED_BLOCKED`
- `MVP_INCONCLUSIVE_NEEDS_MORE_DATA`

Scale decisions remain conservative. If sample size is too low, Phase 14 returns `PILOT_INCONCLUSIVE`.
