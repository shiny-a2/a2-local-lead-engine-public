# Dashboard Plan

Dashboard language from Phase 10 onward must be Persian, RTL, simple, practical, and management-friendly.

| Dashboard | Pages | Allowed Actions | Forbidden Actions | Security |
|---|---|---|---|---|
| Phase 9 Review | queue, detail, edit, final-check, approved, history | edit draft, lock, hold/reject/return, approve for Phase 10 queue | send, schedule, SMTP, inbox sync | private/admin, auth, audit |
| Phase 10 Send | queue, item detail, provider readiness, suppression, unsubscribe, reports | hold/cancel, add suppression, import suppression | send-all, follow-up, inbox, bounce parse, AI reply | Persian RTL, auth, CSRF, no secrets |
| Phase 11 Inbox | messages, detail, bounces, unsubscribes, tasks, timelines | classify/override, suppress, create task, close lead | send reply, follow-up, proposal, call | Persian RTL, auth, no mailbox secrets |
| Phase 12 Opportunity | opportunities, price requests, call requests, guidance, tasks, closed | create human tasks, mark manual action, close | price send, meeting schedule, reply send | Persian RTL, auth, audit |
| Phase 13 Sales | kanban, scope, proposal checklist, internal pricing, followups, tasks, logs | update checklists, log manual comms, approve internal quote manually, close | send quote/proposal/reply, payment link, meeting, call | Persian RTL, auth, no automation |
| Phase 14 Governance | pilot metrics, QA, incidents, runbook, scale gate | mark QA, export reports, record go/no-go | automatic scale/send | Persian RTL, auth, audit |
| Phase 15 Countries | country registry, compliance, source policy, localization, activation | activate/deactivate country manually | auto country expansion | Persian RTL, auth, country gates |
