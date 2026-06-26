# Phase 9 Dashboard Security Policy

The review dashboard is private/admin-only and intended for localhost or a private network. Basic/session auth is required before real use.

No public anonymous access is allowed. API actions are limited to review workflow actions and must never expose secrets or send emails.
