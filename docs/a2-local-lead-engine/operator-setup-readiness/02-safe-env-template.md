# 02 - Safe Env Template

Root template created:

`/.env.operator.example`

Copy it to `.env` only when ready:

```powershell
Copy-Item .env.operator.example .env
```

Key safety defaults in the template:

```env
GLOBAL_OUTREACH_KILL_SWITCH=true
LIVE_API_CALLS_ENABLED=false
LEAD_COLLECTION_ENABLED=false
AI_GENERATION_ENABLED=false
EMAIL_DRAFTING_ENABLED=false
EMAIL_SENDING_ENABLED=false
CONTROLLED_SEND_ENABLED=false
PROVIDER_SEND_ENABLED=false
INBOX_SYNC_ENABLED=false
IMAP_SYNC_ENABLED=false
```

Values Amirali must manually fill before DB-backed dry-run:

```env
DATABASE_URL=
PHASE9_REVIEW_USERNAME=
PHASE9_REVIEW_PASSWORD_HASH=
```

Values required later before live pilot:

```env
DEFAULT_FROM_EMAIL=
DEFAULT_REPLY_TO_EMAIL=
UNSUBSCRIBE_TOKEN_SECRET=
SMTP_HOST=
SMTP_USERNAME=
SMTP_PASSWORD=
```

API keys remain empty until the relevant live phase is explicitly approved.
