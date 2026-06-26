# 04 - Safety Gates And Kill Switch Audit

| Gate | Env key exists | Safe default | Enforced in code | Tests exist | Verdict |
|---|---:|---:|---|---:|---|
| Global kill switch | Yes: `GLOBAL_OUTREACH_KILL_SWITCH` | Yes: `true` | `ControlledSendService.run` blocks commit sends | Yes | PASS |
| Live API calls | Yes: `LIVE_API_CALLS_ENABLED` | Yes: `false` | `app/core/safety.py`, source/verification flows | Yes | PASS |
| Lead collection | Yes: `LEAD_COLLECTION_ENABLED` | Yes: `false` | source collect flow checks it | Yes | PASS |
| AI generation | Yes: `AI_GENERATION_ENABLED` | Yes: `false` | email writer and AI judge config checks | Yes | PASS |
| Email drafting | Yes: `EMAIL_DRAFTING_ENABLED` | Yes: `false` | email writer config checks | Yes | PASS |
| Email judge | Yes: `EMAIL_JUDGE_ENABLED` | Yes: `false` | AI judge optional; rule judge service exists | Yes | PASS |
| Human approval | Yes: `REQUIRE_MANUAL_APPROVAL`, Phase 9 final gates | Yes: `true` | Phase 9 queue/decision/final check services | Yes | PASS |
| Email sending | Yes: `EMAIL_SENDING_ENABLED` | Yes: `false` | controlled send checks before provider call | Yes | PASS |
| Controlled send | Yes: `CONTROLLED_SEND_ENABLED` | Yes: `false` | controlled send checks before provider call | Yes | PASS |
| Provider send | Yes: `PROVIDER_SEND_ENABLED` | Yes: `false` | controlled send checks before provider call | Yes | PASS |
| Inbox sync | Yes: `INBOX_SYNC_ENABLED`, `IMAP_SYNC_ENABLED` | Yes: `false` | mailbox sync blocks commit if gaps | Yes | PASS |
| No auto-price | Phase 12/13 keys exist | Yes: blocking true | human sales control + human-only guard | Yes | PASS |
| No auto-meeting | Phase 12/13 keys exist | Yes: blocking true | meeting guidance + guards | Yes | PASS |
| No auto-reply | Phase 12/13 keys exist | Yes: blocking true | reply suggestions internal only + guards | Yes | PASS |
| No auto-proposal | Phase 12/13 keys exist | Yes: blocking true | customer-facing boundary + guards | Yes | PASS |
| No auto-payment-link | Phase 12/13 keys exist | Yes: blocking true | customer-facing boundary + guards | Yes | PASS |
| Country activation gates | Not found | N/A | Not implemented | Not found | BLOCK |

## Evidence Notes

- `uv run python -m app.cli.main safety check` reported all risky global operations blocked.
- `uv run python -m app.cli.main doctor` reported `risky_operations_disabled: True` but `database: gap: OperationalError`.
- Phase 10 provider call is behind `global_outreach_kill_switch`, `email_sending_enabled`, `controlled_send_enabled`, `provider_send_enabled`, circuit breaker, provider readiness, suppression, limits, cooldown, send window, unsubscribe token, and lock flow.

## Safety Gate Gaps

1. Phase 15 country activation gates are not implemented.
2. Dashboard security gates are weak/inconsistent and should be hardened before any hosted operator use.
3. Current `.env`/runtime config lacks required secrets and provider settings, which is safe but blocks operation.
