# 09 - Amirali Manual Actions

## A. DB Setup

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Create/confirm private Postgres DB | `a2_leads` | Now | BLOCKER |
| Set `DATABASE_URL` in `.env` | `postgresql+psycopg://...` | Now | BLOCKER |
| Back up DB before migration | manual backup path | Before migration | BLOCKER |

## B. Env File Creation

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Copy template | `Copy-Item .env.operator.example .env` | Now | BLOCKER |
| Keep live flags false | see template | Now | BLOCKER |

## C. Dashboard Credentials

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Choose admin username | `amirali-admin` | Now for dashboard | BLOCKER |
| Generate password hash | implementation-specific hash | Now for dashboard | BLOCKER |
| Keep dashboards private/local | VPN/localhost/private route | Now | BLOCKER |

## D. Domain / Unsubscribe URL

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Confirm public unsubscribe URL | `https://amiraliyaghouti.com/unsubscribe` | Before live send | BLOCKER later |
| Generate unsubscribe token secret | long random secret | Before live send | BLOCKER later |

## E. Sender Email Decision

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Choose from email | `hello@amiraliyaghouti.com` | Before live send | BLOCKER later |
| Choose reply-to email | same mailbox | Before live send | BLOCKER later |

## F. cPanel / DNS Readiness

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Configure SPF/DKIM/DMARC | cPanel DNS tools | Before live send | BLOCKER later |
| Fill SMTP env only | host/user/password | Before live send | BLOCKER later |

## G. API Keys

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Geoapify/Tavily/NZBN keys | leave empty for setup | Later | WARNING |
| OpenAI key/model | leave empty for setup | Later | WARNING |

## H. Pilot Country / City / Category

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Confirm NZ/Auckland tiny pilot | New Zealand / Auckland | Now | BLOCKER |
| Confirm first category | barber or beauty salon | Now | BLOCKER |

## I. Backup Path

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Choose backup path | private server path | Before migration | BLOCKER |

## J. Safety Confirmation

| Action | Example | Needed | Verdict |
|---|---|---|---|
| Confirm kill switch true | `GLOBAL_OUTREACH_KILL_SWITCH=true` | Now | PASS |
| Confirm send flags false | all false | Now | PASS |
| Confirm no live API flags | all false | Now | PASS |
