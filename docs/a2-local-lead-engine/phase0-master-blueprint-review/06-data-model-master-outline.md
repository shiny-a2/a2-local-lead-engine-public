# Data Model Master Outline

Do not create migrations in Phase 0. This is a planning outline only.

| Group | Core Entities | Key Relationships |
|---|---|---|
| Foundation/Audit | campaigns, safety_flags, audit_logs, run_contexts, reports | every risky operation references a run and actor |
| Raw Sources | source_runs, source_requests, raw_source_records, source_cache, rate_limits | raw records link to campaign/source run |
| Candidates | candidate_businesses, aliases, source_links, duplicate_clusters, quality_reports | candidates link to raw records and campaign |
| Verification | web_presence_verifications, contact_verifications, contact_candidates, claim_permissions, verified_evidence | candidate-level evidence and claim permissions |
| Scoring | scoring_runs, lead_scores, campaign_fit, readiness_gates, phase5_decisions, pilot_batches | candidate -> score -> decision -> pilot |
| Offers | insight_runs, playbooks, modules, business_insights, pain_points, offer_matches, economic_angles, blocked_claims | Phase 5 ready candidate -> offer package |
| Drafts | email_generation_runs, templates, input_snapshots, subject_candidates, draft_variants, evidence_links, claim_usage, prechecks | Phase 6 offer blocks -> Phase 7 drafts |
| Judge | judge_runs, rule_results, ai_results, findings, decisions, rewrite_briefs, variant_selections | draft variant -> judge decision |
| Review | human_review_runs, queue_items, decisions, edit_versions, final_checks, sender_profiles, mailbox_readiness | judge-approved draft -> Phase 10-ready item |
| Sending | send_queue_runs, send_queue, attempts, provider_configs, circuit_breakers, unsubscribe_tokens/events, suppression_checks, snapshots, locks | Phase 9 approved item -> sent_to_provider snapshot |
| Inbox | inbox_sync_runs, inbound_messages, parts, thread_matches, bounce_events, reply_classifications, lead_statuses, human_tasks, timelines | inbound message -> send/candidate match |
| Opportunity | opportunity_records, response_plans, pricing_guidance, meeting_guidance, followup_eligibility, phase12_tasks, control_gates | classified reply -> manual opportunity |
| Sales Workspace | workspace_items, scope_checklists, proposal_checklists, pricing_worksheets, sales_tasks, communication_logs, health, close_records | opportunity -> human sales workspace |
| Pilot Governance | pilot_metrics, QA findings, ops runbooks, scale_decisions, incident logs | aggregate Phase 1-13 outputs |
| Multi-Country | country_registry, compliance_profiles, source_strategies, send_policies, localization_profiles, activation_gates | country must be active before collection/sending |
