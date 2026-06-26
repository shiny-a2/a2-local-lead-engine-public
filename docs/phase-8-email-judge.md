# Phase 8 Email Judge

Phase 8 judges Phase 7 `JUDGE_PENDING` draft variants before any human approval queue. It checks truthfulness, evidence alignment, claim safety, personalization quality, human-like tone, non-promotional style, economic claim safety, CTA quality, spam risk, and compliance readiness.

In scope:
- deterministic Rule Judge
- optional AI Judge when explicitly enabled
- variant selection
- rewrite briefs as structured guidance
- Markdown, JSON, and CSV reports
- read-only API status endpoints

Out of scope:
- rewriting email bodies
- approving drafts for sending
- sending, SMTP, followups, scheduling, contact forms, social DMs, voice calls
- Tavily, Google Maps, source connectors, or live web verification

Commands:
- `python -m app.cli.main judge emails --campaign auckland-local-website-pilot --run-id <email_generation_run_id> --dry-run`
- `python -m app.cli.main judge emails --campaign auckland-local-website-pilot --run-id <email_generation_run_id> --commit`
- `python -m app.cli.main judge variant --draft-id 1 --dry-run`
- `python -m app.cli.main judge explain --draft-id 1`
- `python -m app.cli.main report judge --run-id <email_judge_run_id>`

Acceptance criteria:
- Rule Judge always runs.
- AI Judge runs only when configured.
- Rule blockers override AI pass decisions.
- Outputs never exceed `APPROVED_FOR_HUMAN_REVIEW`.
- Reports clearly state that no email was sent or approved for sending.
