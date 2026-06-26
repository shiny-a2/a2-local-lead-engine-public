# 11 - Current Env And Config Gaps

## Config Inspection

Commands run:

- `uv run python -m app.cli.main config check`
- `uv run python -m app.cli.main doctor`
- `.env.example` static inspection

No actual secret values were printed. The CLI redacted secret presence as `MISSING` or `PRESENT`.

## Required Keys And Current Status

| Key/group | Present in settings/example | Current detected | Safe default | Recommendation for dry-run | Recommendation for first live pilot |
|---|---:|---|---:|---|---|
| `DATABASE_URL` | Yes | Placeholder; runtime DB failed | No | Configure local/private DB | Required and backed up |
| `LIVE_API_CALLS_ENABLED` | Yes | false | Yes | false | Enable only for tiny source commit window |
| `LEAD_COLLECTION_ENABLED` | Yes | false | Yes | false | Enable only with live source commit |
| `AI_GENERATION_ENABLED` | Yes | false | Yes | false | true only for tiny draft generation if using OpenAI |
| `EMAIL_DRAFTING_ENABLED` | Yes | false | Yes | false | true only for Phase 7 commit |
| `EMAIL_JUDGE_ENABLED` | Yes | false | Yes | rule-only available | optional; AI judge can remain disabled |
| `GLOBAL_OUTREACH_KILL_SWITCH` | Yes | true | Yes | true | false only during tiny live send window |
| `EMAIL_SENDING_ENABLED` | Yes | false | Yes | false | true only immediately before live send |
| `CONTROLLED_SEND_ENABLED` | Yes | false | Yes | false | true only immediately before live send |
| `PROVIDER_SEND_ENABLED` | Yes | false | Yes | false | true only immediately before live send |
| `SMTP_HOST/USERNAME/PASSWORD` | Yes | missing | Yes | missing ok | required env only |
| `DEFAULT_FROM_EMAIL/REPLY_TO` | Yes | empty | Yes | empty ok | required |
| `UNSUBSCRIBE_TOKEN_SECRET` | Yes | missing | No for live | can be missing in local-only tests | required strong secret |
| `OPENAI_API_KEY` | Yes | missing | Yes | missing ok | required only if AI generation/judge used |
| `GEOAPIFY/TAVILY/NZBN` | Yes | missing | Yes | missing ok for plans | required for live source phases as selected |
| `PHASE9_REVIEW_USERNAME/PASSWORD_HASH` | Yes | missing | Not enough for hosted | set before dashboard use | required |
| `INBOX_SYNC_ENABLED/IMAP_SYNC_ENABLED` | Yes | false | Yes | false | true only after inbox setup |
| Phase 12/13 auto-block flags | Yes | blocking true | Yes | keep true | keep true |
| Phase 15 country gates | No | missing | N/A | unavailable | must implement |

## Dangerous Configs

- `PHASE10_SEND_DASHBOARD_ENABLED=true` while dashboard credentials are blank can expose dashboard routes depending on deployment/proxy behavior.
- `UNSUBSCRIBE_TOKEN_SECRET` missing should block real unsubscribe token security readiness.
- `DATABASE_URL` contains placeholder credentials; this is not a real secret exposure, but not operational.

## Recommended First Dry-Run Values

Keep all live/action flags false:

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

## Recommended First Live Pilot Values

Only after all stop points pass:

```env
GLOBAL_OUTREACH_KILL_SWITCH=false
EMAIL_SENDING_ENABLED=true
CONTROLLED_SEND_ENABLED=true
PROVIDER_SEND_ENABLED=true
SEND_PER_RUN_LIMIT=1
SEND_DAILY_LIMIT=3
SEND_PER_DOMAIN_DAILY_LIMIT=1
SEND_WARMUP_MODE=true
```

Then restore kill switch and provider flags after the tiny send window.
