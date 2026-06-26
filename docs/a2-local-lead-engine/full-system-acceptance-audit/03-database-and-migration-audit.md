# 03 - Database And Migration Audit

## Migration Files Found

| Order | File | Phase |
|---:|---|---|
| 1 | `20260525_0001_foundation_schema.py` | Phase 1 |
| 2 | `20260525_0002_phase2_source_intake.py` | Phase 2 |
| 3 | `20260525_0003_phase3_candidates.py` | Phase 3 |
| 4 | `20260525_0004_phase4_verification.py` | Phase 4 |
| 5 | `20260525_0005_phase5_scoring.py` | Phase 5 |
| 6 | `20260525_0006_phase6_insight_offer.py` | Phase 6 |
| 7 | `20260525_0007_phase7_email_writer.py` | Phase 7 |
| 8 | `20260525_0008_phase8_email_judge.py` | Phase 8 |
| 9 | `20260525_0009_phase9_human_review.py` | Phase 9 |
| 10 | `20260525_0010_phase10_controlled_sending.py` | Phase 10 |
| 11 | `20260525_0011_phase11_inbox_reply_crm.py` | Phase 11 |
| 12 | `20260525_0012_phase12_opportunity_planner.py` | Phase 12 |
| 13 | `20260525_0013_phase13_sales_workspace.py` | Phase 13 |

No Phase 14 or Phase 15 migration files were found.

## Table Groups Expected Vs Found

| Group | Evidence found | Verdict |
|---|---|---|
| Foundation/audit | campaigns, leads, audit/safety-related foundation models | PASS |
| Raw sources | source runs, raw records, requests, cache, rate/budget entities | PASS |
| Candidates | candidate businesses, aliases, categories, quality, dedupe/conflicts | PASS |
| Verification | verification runs, web/contact evidence, claim permissions | PASS |
| Scoring | scoring runs, snapshots, lead scores, readiness gates, pilot batch | PASS |
| Offers | insight runs, playbooks, modules, offer matches, safe blocks, blocked claims | PASS |
| Drafts | generation runs, prompt templates/snapshots, inputs, subjects, variants, evidence/claim/precheck/similarity | PASS |
| Judge | judge runs, rule/AI results, findings, decisions, rewrite briefs, variant selections | PASS |
| Review | human review runs/items/decisions, manual edits, final checks, review users/locks, sender/mailbox readiness | PASS |
| Sending | send queue runs/items/attempts, provider config, circuit breaker, unsubscribe, suppression checks, counters, snapshots, locks, audit | PASS |
| Inbox | sync runs, inbound messages/parts/attachments, thread matches, bounces, classifications, tasks, timelines, webhooks | PASS |
| Opportunity | opportunities, response/pricing/meeting guidance, follow-up eligibility, tasks, gates, decisions | PASS |
| Sales workspace | workspace, scope/proposal checklists, pricing worksheet, manual followups, tasks, logs, health, next action, approvals | PASS |
| Pilot governance | expected pilot analytics/QA/runbook/scale decision tables | BLOCK: not found |
| Multi-country | expected country registry/compliance/source/send/localization/activation tables | BLOCK: not found |

## Idempotency / Uniqueness Evidence

- `email_send_queue.idempotency_key` has `UniqueConstraint("idempotency_key", name="uq_send_queue_idempotency")`.
- `unsubscribe_tokens.token_hash` is unique.
- `raw_source_records.fingerprint` is unique.
- `source_cache.cache_key` is unique.
- `opportunity_records.source_inbound_message_id` is unique.
- `sales_workspace_items.opportunity_id` is unique.
- `pilot_batch_candidates` has unique `(batch_name, candidate_business_id)`.

## FK / Model Consistency

Models for Phases 1-13 are present under `app/db/models`. FK relationships were found on major cross-phase entities such as candidate, campaign, draft variant, queue item, send queue, opportunity, and workspace entities. Full Alembic schema application was not run because the configured database is unavailable in this audit environment.

## Audit Tables

Audit/log-style tables exist through Phase 13: `audit_logs`, `human_review_audit_events`, `send_audit_events`, `inbound_audit_events`, `opportunity_audit_events`, and `phase13_audit_events`.

## Gaps

1. No Phase 14 migration/model package.
2. No Phase 15 country registry/compliance/activation model package.
3. Current database was not reachable; migration runtime status is unverified.
4. Some enum values include legacy/foundation names such as `APPROVED_TO_SEND` in `app/core/enums.py`; tests appear to guard against using these in current phase flows, but this should be reviewed before production.
