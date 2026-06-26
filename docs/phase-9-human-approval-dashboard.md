# Phase 9 Human Approval Dashboard

Phase 9 adds a private human review queue between judged drafts and the future controlled send queue. Reviewers can inspect Phase 8-approved drafts, view evidence and judge warnings, create manual edit versions, run final pre-send checks, approve for Phase 10 queue readiness, hold, reject, or return items to Phase 7/8.

Out of scope:
- sending, SMTP, scheduling, followups
- inbox sync, IMAP, bounce processing, delivery tracking
- public dashboard or anonymous review actions

CLI:
- `review build-queue`
- `review approve`
- `review reject`
- `review hold`
- `review return-rewrite`
- `review return-judge`
- `review final-check`
- `report human-review`

Dashboard:
- `/admin/review`
- `/admin/review/items/{id}`
- edit, final check, approval-for-Phase10, return, hold, reject, lock/unlock actions

Approval in Phase 9 means `READY_FOR_PHASE_10_CONTROLLED_SEND_QUEUE` only. It is not permission to send immediately.
