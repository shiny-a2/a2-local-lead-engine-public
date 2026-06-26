# Phase 11 - Inbox, Bounce, Reply CRM

Phase 11 receives and classifies inbound events after controlled sending. It imports sanitized inbound messages, detects replies, bounces, auto replies, unsubscribe-by-reply requests, updates lead response status, creates human tasks, and exposes a private Persian RTL dashboard.

Out of scope: outbound replies, follow-ups, AI reply writing, scheduling, proposal generation, calls, social DMs, and public dashboards.

CLI:
- `python -m app.cli.main inbox plan --mailbox default`
- `python -m app.cli.main inbox sync --mailbox default --dry-run`
- `python -m app.cli.main inbox sync --mailbox default --commit`
- `python -m app.cli.main inbox classify --run-id <sync_run_id> --commit`
- `python -m app.cli.main inbox process-bounces --run-id <sync_run_id> --commit`
- `python -m app.cli.main inbox apply-suppression --run-id <sync_run_id> --commit`
- `python -m app.cli.main report inbox --run-id <sync_run_id>`

Reports clearly state that Phase 11 does not send replies or follow-ups.
