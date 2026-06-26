# Risk Register

| Risk | Severity | Affected Phases | Root Cause | Mitigation | Test / Acceptance Requirement |
|---|---|---|---|---|---|
| Data quality risk | High | 2-6 | noisy public sources, duplicates | provenance, quality scoring, manual review | candidate quality reports and dedupe tests |
| False no-website claim | Critical | 4,7,8 | incomplete search/verification | use cautious wording, claim permissions | block absolute “you don’t have a website” |
| Compliance risk | Critical | 4-15 | unclear AU/NZ/local outreach rules | legal review, unsubscribe, suppression, role emails | compliance boundary tests and reports |
| Spam/deliverability risk | High | 7-10 | too generic/salesy copy or high volume | low volume, warm-up, plain text, human review | spam risk judge and send limits |
| Provider/cPanel risk | High | 9-10 | SMTP acceptance does not guarantee inbox delivery | honest SENT_TO_PROVIDER status, future provider abstraction | delivery unknown modelled clearly |
| Bounce/inbox risk | Medium | 10-11 | cPanel bounce handling limited | manual inbox review, IMAP UID sync later | no delete/read by default tests |
| Duplicate send risk | Critical | 10 | retries/concurrency/candidate dupes | idempotency keys, locks, cooldowns | duplicate guard and lock tests |
| Secret leakage risk | Critical | 1-15 | logs/reports/UI/env mishandling | redaction, env-only secrets, tests | no secrets in DB/log/report assertions |
| Dashboard security risk | High | 9-15 | admin UI exposed publicly | private/local auth, no public actions | auth tests, forbidden route tests |
| AI hallucination/copy risk | High | 7-8 | model invents facts/claims | evidence-bound JSON, precheck, judge | unsupported claims blocked |
| Manual workload risk | Medium | 9-14 | too many review tasks | pilot caps, queues, dashboards | report workload and stop gates |
| Country expansion/legal risk | Critical | 15 | laws/source availability differ | country activation gates | country profile required before activation |

فارسی: ریسک اصلی MVP این است که سیستم زودتر از شواهد و تأیید انسانی وارد ارسال یا ادعای تجاری شود. هر فاز باید fail-closed بماند.
