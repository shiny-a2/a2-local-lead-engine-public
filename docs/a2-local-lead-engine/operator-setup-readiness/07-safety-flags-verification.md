# 07 - Safety Flags Verification

`python -m app.cli.main safety check` reported all risky global operations blocked.

| Flag | Current status | Safe default | Verdict |
|---|---|---|---|
| `GLOBAL_OUTREACH_KILL_SWITCH` | true | true | PASS |
| `LIVE_API_CALLS_ENABLED` | false | false | PASS |
| `LEAD_COLLECTION_ENABLED` | false | false | PASS |
| `AI_GENERATION_ENABLED` | false | false | PASS |
| `EMAIL_DRAFTING_ENABLED` | false | false | PASS |
| `EMAIL_JUDGE_ENABLED` | false | false | PASS |
| `EMAIL_SENDING_ENABLED` | false | false | PASS |
| `CONTROLLED_SEND_ENABLED` | false | false | PASS |
| `PROVIDER_SEND_ENABLED` | false | false | PASS |
| `INBOX_SYNC_ENABLED` | false | false | PASS |
| `IMAP_SYNC_ENABLED` | false | false | PASS |
| `PHASE12_BLOCK_AUTOMATIC_RESPONSE_SEND` | true | true | PASS |
| `PHASE12_BLOCK_AUTOMATIC_MEETING_SCHEDULING` | true | true | PASS |
| `PHASE12_BLOCK_AUTOMATIC_PRICE_QUOTE` | true | true | PASS |
| `PHASE12_BLOCK_AUTOMATIC_PROPOSAL_SEND` | true | true | PASS |
| `PHASE12_BLOCK_AUTOMATIC_PAYMENT_LINK` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_REPLY` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_FOLLOWUP` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_QUOTE` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_MEETING` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_PROPOSAL` | true | true | PASS |
| `PHASE13_BLOCK_PAYMENT_LINK` | true | true | PASS |
| `PHASE13_BLOCK_AUTO_CALL` | true | true | PASS |

Do not change these for operator setup.
