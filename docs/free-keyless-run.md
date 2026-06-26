# Free, Keyless End-to-End Run (no credit card, no paid keys)

This document describes how the A2 Local Lead Engine was wired to run the **entire**
pipeline using only free systems that need **no signup and no credit card**, what was
fixed to make that possible, and the real results from a live run on Auckland data.

The only paid service the project is allowed to use is the OpenAI (GPT) API, and it is
**optional** — the engine drafts emails locally without it.

## Free systems used

| Stage | System | Cost / signup |
|---|---|---|
| Lead collection | OpenStreetMap **Overpass API** | Free, no key, no signup, no card |
| Web-presence verification (Phase 4) | Direct **URL probe** (HTTP HEAD/GET) | Free, no key |
| Email drafting (Phase 7) | **Local template writer** (deterministic) | Free, no key |
| Email judging (Phase 8) | **Rule-only judge** | Free, no key |
| Database | Local **SQLite** file | Free, no server |
| Dashboards / API | FastAPI + uvicorn (localhost) | Free |

Tavily (web search), Geoapify (places), and NZBN remain **optional** upgrades. They are
free-tier and do not require a credit card, but they need an email signup + API key, so
they are off by default. OpenAI is optional and is the only card-requiring service.

> Email **sending stays disabled**. The global kill switch is ON; the send phases only
> produce a dry-run plan. No email is sent to anyone.

## What was fixed / wired to make the free run work

These were real deficiencies — the pipeline looked complete but several "live" paths were
stubs or were starved of data:

1. **OSM connector returned HTTP 406.** The public Overpass instance rejects requests
   without a descriptive `User-Agent`. Added `User-Agent` + `Accept: application/json`
   headers and an automatic fallback mirror. (`app/connectors/osm_overpass.py`)
2. **Phase 4 verification was 100% fake.** `web_presence_decision_orchestrator.py` used a
   hardcoded `_fixture_results()` that fabricated search results and fake emails like
   `info@business.co.nz`. Wired a real, keyless `UrlProbeService` path that probes the
   business's actual website (from the OSM record) and classifies real evidence. Gated by
   the new `PHASE4_LIVE_URL_PROBE` flag. The real source email/phone is now surfaced for
   contact extraction instead of a fabricated one.
3. **Phase 7 was OpenAI-gated.** The email writer blocked the whole run unless an OpenAI
   key was present, even though a deterministic local writer already existed. Added the
   `EMAIL_LOCAL_WRITER_ENABLED` flag so drafting runs for free; OpenAI stays optional.
   (`app/services/email_writer_service.py`)
4. **CLI tied Phase 4 commit to Tavily.** `verify ... --commit` refused to run without a
   Tavily key. Now, when `PHASE4_LIVE_URL_PROBE` is on, it runs the keyless probe path.
   (`app/cli/main.py`)
5. **Candidate builder dropped the city.** OSM POIs usually omit `addr:city`/`addr:country`,
   so every candidate failed the quality gate (`NEEDS_MORE_DATA`). The builder now falls
   back to the queried city/country recorded on the source run.
   (`app/services/candidate_builder_service.py`)
6. **Database was unconfigured.** Added a minimal `.env` pinning a local SQLite database so
   no Postgres server is needed. (The `.env` is intentionally minimal so the test suite,
   which asserts safe defaults, stays green.)

All 482 tests still pass, `ruff` is clean.

## How to run it

```bash
# one-time: install deps (uv)
uv sync --all-extras

# run the whole free pipeline (live OSM -> ... -> Phase 9 review queue; sending stays dry-run)
bash scripts/run_local_pipeline.sh Auckland beauty_salon 60
#                                   ^city    ^category     ^limit
# categories: barber | beauty_salon | cleaning_service
```

## Countries & cities

A registry of countries with big and small cities lives in `app/config/geography.yaml`
(12 countries, ~180 cities: NZ, Australia, UK, Ireland, Canada, Germany, France,
Netherlands, Spain, Italy, UAE, Turkey). The OSM connector resolves any city worldwide by
matching its local name, English name (`name:en`), or a "City/Council"-style prefix, and
disambiguates by ISO country code (so Sydney AU never pulls in Sydney CA).

```bash
.venv/Scripts/python.exe -m app.cli.main geo countries
.venv/Scripts/python.exe -m app.cli.main geo cities --country Germany --size big
# run the whole pipeline across every city of a country:
bash scripts/run_country_pipeline.sh "Australia" big beauty_salon 25
```

## Email sending service

Sending uses your own domain via cPanel SMTP (free). See `docs/email-sending-setup.md`.
Free deliverability + self-test commands (no key, nothing sent to leads):

```bash
.venv/Scripts/python.exe -m app.cli.main send dns-check --domain amiraliyaghouti.com
.venv/Scripts/python.exe -m app.cli.main send self-test --to you@amiraliyaghouti.com   # add --commit to send
```

Reports land in `reports/`. To prove the keyless drafting chain (Phase 6→7→8→9) end to
end without any key:

```bash
.venv/Scripts/python.exe scripts/demo_local_draft.py
```

## Real run results (Auckland beauty salons, 60 leads, live)

The engine collected 60 real Auckland beauty businesses from OpenStreetMap and verified
them with real URL probes:

| Phase 4 web status (real probe) | Count |
|---|---:|
| `WEBSITE_FOUND_OFFICIAL` (live site → correctly rejected, already has one) | 19 |
| `NO_WEBSITE_PROBABLE` (the target leads) | 40 |
| `SOCIAL_ONLY` | 1 |

| Phase 4 decision | Count |
|---|---:|
| `READY_FOR_PHASE_5_SCORING` | 40 |
| `REJECT_WEBSITE_ALREADY_STRONG` | 19 |
| `REJECT_COMPLIANCE_RISK` (personal email) | 1 |

Phase 5 then **held all 40** no-website leads at `HOLD_NO_SAFE_CONTACT`.

### Why the funnel ends in "hold", and what that means

This is the engine behaving **correctly**, not a failure:

- The compliance rules deliberately **block personal / free-provider emails**
  (gmail/yahoo/outlook and `firstname`-style addresses). Only role-based business emails
  on a business's own domain (e.g. `bookings@salon.co.nz`) are outreach-eligible.
- OpenStreetMap rarely carries such emails for hairdressers/beauty/cleaning. So the honest
  free-data outcome is a **vetted list of no-website businesses pending contact discovery**,
  not a pile of ready-to-send emails. The system refuses to invent a contact.

To turn these vetted leads into send-ready drafts you add a contact source (both optional):

- a **free Tavily API key** (free tier, no card) to search for each business's contact, or
- a human/manual contact import for the shortlisted leads.

The drafting → judging → human-review chain itself is fully working and free (proven by
`scripts/demo_local_draft.py`: local draft → rule-judge `APPROVED_FOR_HUMAN_REVIEW` →
queued for human review, with no OpenAI and nothing sent).

## Enable real AI drafting (optional, GPT — the only paid service)

The email writer now has a real OpenAI client (`app/services/openai_client.py`, via httpx —
no extra SDK). Without a key it uses the free local template; with a key it calls GPT.

Put the key in `.env` (safe for tests — only the boolean AI flags must NOT go in `.env`,
they are set per-run by the pipeline script):

```env
OPENAI_API_KEY=sk-...
OPENAI_EMAIL_MODEL=gpt-4o-mini
```

Then just run the pipeline — it auto-detects the key and switches the writer to GPT:

```bash
OPENAI_API_KEY=sk-... bash scripts/run_local_pipeline.sh Auckland beauty_salon 60
# the script prints: (email writer: OpenAI GPT, model=gpt-4o-mini)
```

The generated drafts still pass through the same rule-judge and human-review queue; nothing
is sent.

## Safety posture (unchanged)

`GLOBAL_OUTREACH_KILL_SWITCH=true`, `EMAIL_SENDING_ENABLED=false`,
`CONTROLLED_SEND_ENABLED=false`, `PROVIDER_SEND_ENABLED=false`. The send phases only ever
produce a dry-run plan. Enabling real sending is a separate, deliberate operator decision.
