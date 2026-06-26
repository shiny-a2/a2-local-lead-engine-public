# Safety Gates Master Policy

| Gate | Default | Blocks |
|---|---|---|
| global kill switch | ON / blocking | all live outreach and send paths |
| live API calls gate | OFF | Geoapify/Tavily/NZBN/other external calls |
| lead collection gate | OFF | raw lead collection |
| AI generation gate | OFF | OpenAI drafting/classification/judging |
| email drafting gate | OFF until Phase 7 | draft creation |
| email judge gate | OFF or rule-only until configured | optional AI judge |
| human approval gate | REQUIRED | Phase 10 send queue entry |
| email sending gate | OFF until Phase 10 | SMTP/provider send |
| provider send gate | OFF until configured | provider call |
| unsubscribe gate | REQUIRED | sending without body/header unsubscribe |
| suppression gate | REQUIRED | sending to suppressed email/domain |
| duplicate send gate | REQUIRED | repeated candidate/recipient/campaign send |
| country activation gate | REQUIRED for Phase 15 | source and send in inactive country |
| no-auto-price gate | REQUIRED | automatic price/quote |
| no-auto-meeting gate | REQUIRED | calendar/meeting automation |
| no-auto-reply gate | REQUIRED | outbound reply automation |
| no-auto-proposal gate | REQUIRED | proposal generation/sending automation |
| no-auto-payment-link gate | REQUIRED | payment link creation |

Every risky gate must be testable, audited, and fail-closed. Dry-run must not call providers or send messages.
