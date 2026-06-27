# Real-business sending: readiness & the path to GO

An adversarial pre-send audit (multi-agent) returned **NO_GO** for sending cold emails to
real businesses. This document records why, and the exact steps to reach a safe GO. The
engine runs end-to-end and emails are visible in the dashboard; what is held is the final
**send to third-party businesses**. (A real preview email is sent only to your own inbox.)

## Why NO_GO (must-fix before any real-business send)

1. **Opt-out is not honoured automatically.** The unsubscribe is reply/mailto based (the
   public web page 404s). A recipient who replies "UNSUBSCRIBE" is only suppressed if inbound
   mail is processed, but `INBOX_SYNC_ENABLED` / `IMAP_SYNC_ENABLED` are off. Without this, an
   opt-out is silently dropped and the contact could be re-emailed — a breach of NZ/AU/US law.

2. **Country gate is off by default.** `COUNTRY_COMPLIANCE_ENFORCED` defaults to false, so a
   batch run with defaults would not block opt-in countries (EU/Turkey/UAE). Must be ON and
   verified before any send. Also: `country` is free text — only exact matches (e.g. "New
   Zealand") are recognised; "NZ"/"Aotearoa" fall through to the safe default (blocked).

3. **Relevance/right-business check must be on AND keyed.** The AI relevance agent only runs
   when `EMAIL_RELEVANCE_AGENT_ENABLED=true` and an OpenAI key is present (it now fails CLOSED
   to manual review otherwise). The rule judge alone does not verify the email is about the
   right business.

## What was already fixed for compliance

- Recipient is the candidate's verified, outreach-allowed email (no placeholder).
- `ContactRelevanceService` drops wrong-business discovered emails (foreign-TLD same-name like
  `queennails.dk` for an Auckland salon, and directory/aggregator domains like `findmylocal.nz`).
- `List-Unsubscribe: <mailto:...?subject=Unsubscribe>` + a reply-UNSUBSCRIBE line in every body.
- `UNSUBSCRIBE_TOKEN_SECRET` set.
- Suppression already blocks future sends and stops follow-ups for opted-out contacts.

## The path to a safe GO (small NZ-only warm-up)

1. **Honour opt-outs automatically** — either deploy the FastAPI `/unsubscribe` endpoint at a
   reachable URL and set `UNSUBSCRIBE_ONE_CLICK_ENABLED=true`, **or** set live IMAP creds
   (`IMAP_HOST/USERNAME/PASSWORD`, `INBOX_SYNC_ENABLED=true`) and run, daily,
   `inbox sync --commit` → `inbox classify --commit` so reply-UNSUBSCRIBE becomes suppression
   within 5 business days.
2. **Enforce the country gate**: `COUNTRY_COMPLIANCE_ENFORCED=true`; restrict the batch to leads
   whose stored country is exactly an allowed key (e.g. "New Zealand").
3. **Enforce relevance**: `EMAIL_RELEVANCE_AGENT_ENABLED=true` with the OpenAI key set.
4. **Human-approve each email** in the dashboard / review queue (the Phase 9 design), then send a
   tiny warm-up (`SEND_PER_RUN_LIMIT` ~3, `SEND_PER_DOMAIN_DAILY_LIMIT=1`, warmup on).
5. Re-run the pre-send audit; only send when it returns GO.
