# 01 - Env Required Values

Status values show presence only. No raw secrets are shown.

| Group | Key | Dry-run required | Live pilot required | Safe default | Current status | Notes |
|---|---|---:|---:|---|---|---|
| app/runtime | `APP_ENV` | Yes | Yes | `development` | PRESENT | Use private/local deployment first |
| app/runtime | `APP_TIMEZONE` | Recommended | Yes | `Pacific/Auckland` | PRESENT | Align pilot send window |
| database | `DATABASE_URL` | Yes | Yes | none | PRESENT_PLACEHOLDER / NOT_CONNECTED | Must be replaced in `.env` |
| dashboard auth | `PHASE9_BASIC_AUTH_ENABLED` | Yes | Yes | `true` | PRESENT | Keep true |
| dashboard auth | `PHASE9_REVIEW_USERNAME` | Yes for dashboard | Yes | empty | MISSING | Required before hosted use |
| dashboard auth | `PHASE9_REVIEW_PASSWORD_HASH` | Yes for dashboard | Yes | empty | MISSING | Required before hosted use |
| safety flags | `GLOBAL_OUTREACH_KILL_SWITCH` | Yes | Yes | `true` | PRESENT_SAFE | Must remain true for setup/dry-run |
| safety flags | `LIVE_API_CALLS_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| safety flags | `LEAD_COLLECTION_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| safety flags | `AI_GENERATION_ENABLED` | Yes | Later if AI used | `false` | PRESENT_SAFE | Keep false |
| safety flags | `EMAIL_DRAFTING_ENABLED` | Yes | Later if AI used | `false` | PRESENT_SAFE | Keep false |
| safety flags | `EMAIL_SENDING_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| safety flags | `CONTROLLED_SEND_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| safety flags | `PROVIDER_SEND_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| safety flags | `INBOX_SYNC_ENABLED` | Yes | Later | `false` | PRESENT_SAFE | Keep false |
| OpenAI | `OPENAI_API_KEY` | No | Required for AI drafting/judge | empty | MISSING | Do not fill until AI phase is approved |
| OpenAI | `OPENAI_EMAIL_MODEL` | No | Required if drafting | empty | MISSING | Manual choice |
| sources | `GEOAPIFY_API_KEY` | No | Required for live Geoapify | empty | MISSING | Do not use yet |
| sources | `TAVILY_API_KEY` | No | Required for live Tavily | empty | MISSING | Do not use yet |
| sources | `NZBN_API_KEY` | No | Required for live NZBN | empty | MISSING | Do not use yet |
| email sender | `DEFAULT_FROM_EMAIL` | No | Yes | empty | MISSING | Required before live send |
| email sender | `DEFAULT_REPLY_TO_EMAIL` | No | Yes | empty | MISSING | Required before live send |
| unsubscribe | `UNSUBSCRIBE_PUBLIC_BASE_URL` | Recommended | Yes | domain URL | PRESENT | Confirm final URL |
| unsubscribe | `UNSUBSCRIBE_TOKEN_SECRET` | No | Yes | empty | MISSING | Required before live send |
| SMTP/cPanel | `SMTP_HOST` | No | Yes | empty | MISSING | Env only, never DB |
| SMTP/cPanel | `SMTP_USERNAME` | No | Yes | empty | MISSING | Env only |
| SMTP/cPanel | `SMTP_PASSWORD` | No | Yes | empty | MISSING | Env only |
| inbox/IMAP | `IMAP_HOST` | No | Phase 11 live sync | empty | MISSING | Keep sync disabled |
| inbox/IMAP | `IMAP_USERNAME` | No | Phase 11 live sync | empty | MISSING | Keep sync disabled |
| inbox/IMAP | `IMAP_PASSWORD` | No | Phase 11 live sync | empty | MISSING | Env only |
| paths | reports/exports/logs | Yes | Yes | local dirs | PRESENT_WRITABLE | Probes passed |
| country/campaign | `PHASE15_BOUNDARY_STATUS` | Yes | Yes | post-MVP NZ tiny pilot | PRESENT | Does not claim multi-country readiness |
