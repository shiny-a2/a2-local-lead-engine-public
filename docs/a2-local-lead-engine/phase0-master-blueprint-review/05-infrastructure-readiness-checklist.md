# Infrastructure Readiness Checklist

| Area | Checklist | Status Before Phase 1 |
|---|---|---|
| Alphacore VPS | SSH access, firewall, private ports, deploy path | Required |
| Python | Python 3.12+, uv/pip tooling | Required |
| Database | existing DB reachable, backup plan, migration user | Required |
| Env vars | `.env.example`, secret redaction, no secrets in git | Required |
| OpenAI API | key available, model names chosen, disabled by default | Before Phase 7 |
| Geoapify | free key and quota understood | Before Phase 2 live collection |
| Tavily | free key and quota understood | Before Phase 4 search |
| NZBN | access confirmed for NZ enrichment | Before Phase 2 NZBN |
| cPanel email | mailbox exists, SMTP host/port known | Before Phase 10 |
| DNS | SPF, DKIM, DMARC, reply-to | Before Phase 10 live send |
| Unsubscribe | public URL and token secret | Before Phase 10 |
| Dashboard access | private/admin only, auth, no public anonymous access | Before Phase 9 |
| Backups | DB and reports backup path | Before Phase 2 live data |
| Logs/reports | writable path, retention, redaction | Phase 1 |

No production send readiness exists until Phase 10 gates confirm sender/provider/unsubscribe/suppression/limits.
