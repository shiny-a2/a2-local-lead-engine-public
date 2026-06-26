# Phase 0 Executive Summary

## Project
A2 Local Lead Intelligence & Email Outreach Engine is intended to find local businesses, verify public evidence, prepare evidence-bound outreach, send only human-approved low-volume email, process inbound replies/bounces, and support manual sales operations.

## MVP Boundary
The MVP is email-only. Voice, calls, social DMs, Google Maps/Places, automatic pricing, meeting scheduling, proposal sending, payment links, and automated follow-ups are outside MVP. Phase 10 is the first phase allowed to send email, and only after human approval, suppression, unsubscribe, duplicate, provider, send-limit, and kill-switch gates pass.

## Safety Model
The roadmap is safety-first and fail-closed:

| Safety Area | Required Position |
|---|---|
| Evidence | No claim without evidence or claim permission |
| Sending | No send before Phase 10 and no send without human approval |
| Compliance | Unsubscribe, suppression, truthful claims, manual legal review |
| AI | Drafting/judging only when flags allow; no AI sales automation |
| Operations | Dry-run first, audit logs, reports, kill switches |
| Sales | Human-only pricing, replies, meetings, proposals, decisions |

## Final Roadmap View
Phases 1-14 form the MVP path from foundation through pilot governance. Phase 15 is post-MVP expansion and must not be mixed into the first pilot.

## Conservative Readiness Verdict
`READY_TO_START_PHASE_1_WITH_DECISIONS`

Phase 1 can start once the first implementation decisions in `04-missing-decisions-and-questions.md` are answered or explicitly deferred. No production lead collection, drafting, or sending should start from Phase 0.
