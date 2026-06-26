# Phase 7 Email Writer

Phase 7 creates short, natural, evidence-bound draft variants for Phase 8 review.

It does not approve, schedule, or send emails. Highest draft state is `JUDGE_PENDING`.

Commands:
- `python -m app.cli.main email generate --campaign auckland-local-website-pilot --limit 10 --dry-run`
- `python -m app.cli.main email generate --campaign auckland-local-website-pilot --limit 10 --commit`
- `python -m app.cli.main email explain --draft-id 1`
- `python -m app.cli.main report email-generation --run-id <run_id>`
