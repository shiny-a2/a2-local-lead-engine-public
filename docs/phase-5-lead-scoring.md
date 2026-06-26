# Phase 5 Lead Scoring

Goal: score Phase 4 verified candidates for Phase 6 insight/offer planning only.

In scope: campaign lane selection, readiness gates, explainable score components, priority tiers, pilot batch CSV, and reports.

Out of scope: email writing, subject generation, AI calls, Tavily/search, SMTP, sending, contact form submission, social DMs, Google Maps, voice, offers, and final outreach approval.

Flow:
1. Read candidates with Phase 4 READY_FOR_PHASE_5_SCORING or READY_FOR_PHASE_5_WITH_WARNINGS.
2. Apply hard gates before final readiness.
3. Compute versioned score components.
4. Assign campaign lane and priority tier.
5. Build an optional P1/P2 pilot batch for Phase 6.

Commands:
- `python -m app.cli.main score candidates --campaign auckland-local-website-pilot --limit 50 --dry-run`
- `python -m app.cli.main score candidates --campaign auckland-local-website-pilot --limit 50 --commit`
- `python -m app.cli.main score explain --candidate-id 1`
- `python -m app.cli.main pilot build-batch --campaign auckland-local-website-pilot --batch-name "Auckland Pilot Batch 001" --limit 25 --dry-run`
- `python -m app.cli.main report scoring --run-id <run_id>`

Acceptance: reports must state that Phase 5 does not generate, approve, or send outreach.
