# Phase 6 Insight Offer Engine

Goal: prepare structured business insights and offer ingredients for Phase 7.

In scope: category playbooks, module selection, economic value angles, price positioning guidance, implementation feasibility notes, future email offer fragments, readiness gates, and reports.

Out of scope: email body writing, subject lines, AI calls, live search, sending, SMTP, proposals, pricing quotes, contact forms, social DMs, Google Maps, and voice.

Commands:
- `python -m app.cli.main insight generate --campaign auckland-local-website-pilot --limit 25 --dry-run`
- `python -m app.cli.main insight generate --campaign auckland-local-website-pilot --limit 25 --commit`
- `python -m app.cli.main offer match --campaign auckland-local-website-pilot --limit 25 --dry-run`
- `python -m app.cli.main offer explain --candidate-id 1`
- `python -m app.cli.main report insights --run-id <run_id>`

Outputs are ingredients only. They do not authorize outreach.
