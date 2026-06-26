# 10 - First Run Step By Step Runbook

Never start with live send. The first run must be staged, tiny, dry-run-first, and manually reviewed.

## Sequence

1. `uv run python -m app.cli.main doctor`
2. `uv run python -m app.cli.main config check`
3. `uv run python -m app.cli.main safety check`
4. Fix DB/env gaps until doctor shows DB ok and risky operations blocked.
5. `uv run python -m app.cli.main db upgrade`
6. `uv run python -m app.cli.main campaign seed`
7. `uv run python -m app.cli.main sources check`
8. Source dry-run only:
   `uv run python -m app.cli.main collect geoapify --campaign auckland-local-website-pilot --city Auckland --country "New Zealand" --category barber --limit 3 --dry-run`
9. `STOP_AND_REVIEW` source plan/report.
10. If approved, run a tiny source commit only with live API and lead collection flags intentionally enabled, limit 3, then immediately disable again.
11. Normalize dry-run and then commit only if raw records look safe.
12. Verification dry-run.
13. `STOP_AND_REVIEW` verification/evidence/claim permissions.
14. Verification commit only if allowed and configured.
15. Score dry-run, inspect pilot candidate list.
16. Offer/insight dry-run, inspect safe offer blocks.
17. Email generation dry-run. Confirm no OpenAI call in dry-run.
18. If AI drafting is intentionally enabled later, generate only tiny batch.
19. `STOP_AND_REVIEW` email drafts and evidence mapping.
20. Run judge dry-run, then commit judge only after draft review.
21. Build review queue dry-run, then review in dashboard/private CLI.
22. Human final pre-send checks.
23. Build send queue dry-run.
24. `STOP_AND_REVIEW` before any send. Confirm suppression, unsubscribe, provider readiness, limits, cPanel delivery-unknown note.
25. Tiny live send only if all gates pass: max 1 email first, then stop.
26. `STOP_AND_REVIEW` after first send-to-provider.
27. Inbox plan and dry-run sync only; do not mark read/delete/move.
28. Pilot report and manual review.

## Live Send Guardrail

For the first live pilot, do not exceed 1-3 emails. Never use a bulk/send-all action. Keep all follow-up/reply/proposal/quote/meeting/payment automation disabled.

## Missing Step

Phase 14 governance commands are not available. Implement or create a manual governance workaround before declaring live pilot readiness.
