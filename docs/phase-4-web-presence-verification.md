# Phase 4 Web Presence Verification

Goal: verify web presence, contact evidence, claim permissions, and readiness for Phase 5
scoring. Phase 4 does not authorize outreach, write email, send messages, call AI, use Google
Maps, submit forms, or create sales scores.

CLI:

- `python -m app.cli.main verify plan --campaign auckland-local-website-pilot --limit 25`
- `python -m app.cli.main verify websites --campaign auckland-local-website-pilot --dry-run`
- `python -m app.cli.main verify contacts --campaign auckland-local-website-pilot --dry-run`
- `python -m app.cli.main verify full --campaign auckland-local-website-pilot --dry-run`
- `python -m app.cli.main report verification --run-id <verification_run_id>`

Outputs include verification runs, search plans, web presence decisions, contact candidates,
claim permissions, verified evidence, decisions for Phase 5 scoring, and manual review exports.

