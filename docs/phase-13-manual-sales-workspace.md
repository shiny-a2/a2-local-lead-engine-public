# Phase 13 Manual Sales Workspace

Phase 13 turns Phase 12 opportunities into a private Persian RTL workspace for human-led sales operations.

It creates sales workspace items, scope checklists, proposal checklists, internal pricing worksheets, manual-only follow-up plans, sales tasks, communication logs, opportunity health snapshots, next human actions, close reason records, human approval ledger rows, and reports.

Out of scope:
- no reply sending
- no follow-up sending
- no customer-facing quote generation
- no proposal generation or sending
- no meeting scheduling
- no payment links
- no calls or voice automation
- no external API calls

CLI:
- `python -m app.cli.main sales-workspace build --campaign auckland-local-website-pilot --dry-run`
- `python -m app.cli.main sales-workspace build --campaign auckland-local-website-pilot --commit`
- `python -m app.cli.main sales-workspace explain --opportunity-id <id>`
- `python -m app.cli.main report sales-workspace --campaign auckland-local-website-pilot`

Final verdict target: `PHASE_13_MANUAL_SALES_WORKSPACE_READY`.
