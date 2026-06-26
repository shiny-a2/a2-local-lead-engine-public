# 02 - CLI Command Inventory

Source: `app/cli/main.py` and `app/cli/sales_workspace.py`.

| Group | Commands found | Dry-run | Commit/live | Safety flags / gates | External side effect risk | Audit verdict |
|---|---|---:|---:|---|---|---|
| Foundation | `doctor`, `db upgrade`, `config check`, `campaign seed`, `safety check`, `report foundation`, `fixtures seed` | Partial | Yes for DB/report/fixture commands | DB/env required | DB writes for seed/fixtures/report | PASS with operator caution |
| Source/raw intake | `sources list`, `sources check`, `collect geoapify`, `collect osm`, `enrich nzbn`, `report source-run`, `report raw-quality` | Yes | Yes for collect/enrich | `LIVE_API_CALLS_ENABLED`, `LEAD_COLLECTION_ENABLED`, source budgets/key checks | External API calls only on commit with gates | PASS |
| Normalization | `normalize run`, `normalize rebuild`, `dedupe run`, `quality candidates`, `evidence consolidate`, `report candidates`, `report manual-review` | Yes where applicable | Yes | DB/campaign context | DB writes on commit | PASS |
| Verification | `verify plan`, `verify websites`, `verify contacts`, `verify full`, `report verification` | Yes | Yes | verification flags, live API gates for Tavily/search if used | Live URL/search calls if enabled | PASS, not live-tested |
| Scoring | `score candidates`, `score explain`, `campaign select`, `pilot build-batch`, `report scoring` | Yes for candidate scoring/build | Yes | prior phase readiness | DB writes only | PASS |
| Offer/insight | `insight generate`, `offer match`, `offer explain`, `report insights` | Yes/commit pattern in service | Yes | Phase 5/6 readiness | DB writes only | PASS |
| Email generation | `email generate`, `email explain`, `report email-generation` | Yes | Yes | `AI_GENERATION_ENABLED`, `EMAIL_DRAFTING_ENABLED`, OpenAI key/model | OpenAI call only when enabled/commit | PASS |
| Judge | `judge emails`, `judge variant`, `judge explain`, `report judge` | Yes | Yes | Rule judge always; AI judge flags/key/model | Optional OpenAI judge only if enabled | PASS |
| Review | `review build-queue`, `review export`, `review approve`, `review reject`, `review hold`, `review return-rewrite`, `review return-judge`, `review export-edit-template`, `review import-edit`, `review final-check`, `report human-review` | Queue build supports dry-run | Yes | final pre-send, suppression/contact/sender gates | DB writes only; no send | PASS |
| Send | `send build-queue`, `send provider-check`, `send run`, `send suppress`, `send suppress-domain`, `send suppression-import`, `send hold-item`, `send cancel-item`, `report sending` | Yes for queue/run/import | Yes | kill switch, sending flags, provider flag, suppression, unsubscribe, limits, locks | SMTP provider call only in `send run --commit` with gates | WARNING: live command exists; keep disabled until setup. |
| Inbox | `inbox plan`, `inbox sync`, `inbox classify`, `inbox process-bounces`, `inbox apply-suppression`, `inbox override`, `report inbox` | `sync --dry-run`; plan no import | Yes for writes | `INBOX_SYNC_ENABLED`, `IMAP_SYNC_ENABLED`; no delete/mark-read defaults | IMAP read only when enabled/commit | PASS, not live-tested |
| Opportunity | `opportunity build`, `plan-response`, `explain`, `close`, `report opportunities` | build supports dry-run | Yes | human-only boundaries | DB writes only | PASS |
| Sales workspace | `sales-workspace build`, `explain`, `create-scope-checklist`, `create-proposal-checklist`, `update-scope-item`, `update-proposal-item`, `update-pricing`, `approve-quote-manually`, `log-manual-communication`, `close`, `report sales-workspace` | build supports dry-run | Yes | human-only guard, customer-facing boundary | DB writes only; logs manual external actions only | PASS |
| Pilot governance | None found | No | No | N/A | N/A | BLOCK |
| Country expansion | None found | No | No | N/A | N/A | BLOCK |

## Notes

- `make` targets exist but `make` is not installed on this Windows host.
- Commands with `--commit` should be considered DB-mutating even when they do not call external APIs.
- No command should be run live until the operator checklist is complete.
