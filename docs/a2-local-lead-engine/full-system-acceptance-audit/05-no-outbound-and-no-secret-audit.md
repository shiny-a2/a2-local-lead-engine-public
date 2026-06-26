# 05 - No-Outbound And No-Secret Audit

## Dangerous-Term Grep Summary

The required grep terms were searched across `app`, `docs`, `tests`, and `.env.example`. Most hits are expected policy/test/blocked-claim references. No unauthorized send-all, auto-reply, auto-quote, auto-proposal, payment-link creation, Google Maps API, calendar automation, voice automation, or direct OpenAI leakage implementation was found.

## Findings

| Severity | Finding | Evidence | Assessment | Recommended fix |
|---|---|---|---|---|
| WARNING | SMTP send code exists | `app/services/cpanel_smtp_provider.py:44-45` uses `smtp.login` and `smtp.send_message` | Expected Phase 10 provider implementation. It is gated by `ControlledSendService`, but must remain CLI-first and disabled until configured. | Keep tests and gate checks; do not expose dashboard send actions. |
| WARNING | Controlled send selects `READY_TO_SEND_CONTROLLED` | `app/services/controlled_send_service.py:52` | Expected Phase 10 state, not forbidden `READY_TO_SEND`/`APPROVED_TO_SEND`. | No fix needed. |
| WARNING | Legacy enum value `APPROVED_TO_SEND` exists | `app/core/enums.py:81` | Potential naming confusion from early foundation enum. Tests indicate current flows do not create send-ready approvals. | Consider deprecating or isolating legacy enum before production. |
| BLOCKER | Dashboard auth is not production-grade | `app/services/dashboard_auth_service.py:13-18`, `app/web/send_routes.py:21-31` | Header-only/username-only checks; Phase 10 send dashboard may not require auth when username is blank. | Implement consistent session/basic auth with password hash and CSRF before hosted use. |
| WARNING | Persian text mojibake in inline dashboard strings/templates | `app/web/send_routes.py`, `app/templates/inbox/mailbox_readiness.html` | UI may be unreadable despite `lang=fa`/`dir=rtl`. | Re-save route/template strings as proper UTF-8 Persian and prefer templates over inline HTML. |
| INFO | Secret env keys appear in tests/docs | e.g. `tests/test_redaction.py`, `.env.example` | Test values are fake and redaction tests confirm `PRESENT`/`MISSING` behavior. | No action except avoid real secrets in committed files. |
| INFO | Blocked claims appear in tests/services | `you don't have a website`, `stop paying commissions`, `guaranteed bookings` | These are used as negative test cases and blocked terms. | No fix needed. |
| INFO | `requests.post` appears in Tavily service | `app/services/tavily_search_service.py` | Expected connector behavior behind config/safety gates; not run in audit. | Keep live API flags disabled until source phase dry-run/commit approval. |

## Secret Handling

- `Settings.safe_dict()` redacts secrets as `PRESENT`/`MISSING`.
- `config check` output did not expose secret values.
- SMTP password is not stored in provider DB metadata; provider readiness notes state this.
- Unsubscribe tokens store token hash only; raw token is generated for URL creation.

## Outbound Automation Verdict

**PASS with dashboard-auth hardening required.** No unauthorized outbound automation was found, but real SMTP capability exists by design and must remain gated.
