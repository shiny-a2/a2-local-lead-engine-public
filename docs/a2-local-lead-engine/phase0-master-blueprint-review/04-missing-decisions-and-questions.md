# Missing Decisions And Questions

| Decision | Required Before | Options / Notes | Owner |
|---|---|---|---|
| Final database | Phase 1 | PostgreSQL on Alphacore vs local SQLite dev only | Amirali |
| Dashboard domain/access | Phase 1/9 | private VPS route, VPN, basic auth, reverse proxy | Amirali |
| Unsubscribe domain | Phase 10 | amiraliyaghouti.com/unsubscribe or subdomain | Amirali |
| Sender email | Phase 9/10 | hello@amiraliyaghouti.com vs amirali@ | Amirali |
| Provider | Phase 10 | cPanel SMTP first, future Postmark/SES/Mailgun | Amirali |
| First pilot country/city | Phase 2 | suggested Auckland NZ only | Amirali |
| First categories | Phase 2/6 | beauty_salon, barber, cleaning_service; cafe draft | Amirali |
| OpenAI model names | Phase 7/8 | email model and judge model | Amirali |
| First pilot volume | Phase 5/10 | recommended 10-25 queue, 5 sends/run max | Amirali |
| Dashboard auth model | Phase 9 | basic auth MVP vs session auth | Amirali |
| Backup location | Phase 1 | VPS path, offsite archive, retention | Amirali |
| Legal/compliance boundary | Phase 0/10 | manual legal review needed; code is not legal advice | Amirali |
| DNS readiness | Phase 10 | SPF/DKIM/DMARC manual checks | Amirali/cPanel |
| Reply mailbox | Phase 11 | manual inbox vs IMAP sync | Amirali |
| Logging retention | Phase 1 | audit/log/report retention days | Amirali |

Blocker if not answered: sender identity, unsubscribe URL, suppression policy, initial pilot geography/category, database target, dashboard auth, and legal review boundary.
