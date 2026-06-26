# Phase 10 Controlled Sending

Phase 10 creates a controlled send queue from Phase 9-ready drafts. It can send only through CLI `send run --commit` when the global kill switch is off and all sending flags are enabled.

It includes provider abstraction, suppression enforcement, unsubscribe links, limits, cooldowns, transactional locks, provider circuit breaker, message snapshots, Persian RTL dashboard, and reports.

Out of scope: followups, inbox sync, IMAP, bounce parsing, delivery guarantee, tracking pixels, click tracking, HTML email, attachments, social DMs, voice, Google Maps, and source connectors.
