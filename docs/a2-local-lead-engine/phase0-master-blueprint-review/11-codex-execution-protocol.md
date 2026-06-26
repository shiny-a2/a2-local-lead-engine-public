# Codex Execution Protocol

For every implementation phase Codex must:

1. Read Phase 0 and prior phase docs.
2. Implement only the current phase.
3. Avoid jumping ahead or adding forbidden features.
4. Preserve fail-closed safety flags.
5. Avoid external APIs unless the phase explicitly allows them and flags permit them.
6. Never expose secrets in code, logs, reports, UI, tests, or output.
7. Add focused tests proportional to risk.
8. Run migrations and tests where possible.
9. Generate phase reports.
10. List files changed, migrations, commands run, test results, gaps, blockers, and final verdict.
11. Never claim implementation beyond the current phase.
12. If a user asks for a later phase, treat it as the active phase only after confirming prerequisites exist.

Codex must use conservative verdicts and must not hide failed tests, migration failures, config gaps, or legal/compliance unknowns.
