# Phase 10 Security And Secret Handling Policy

SMTP passwords and provider API keys are read from environment variables only. They must not appear in DB rows, CLI output, UI, reports, logs, or tests.

Dashboard actions require private/admin access and should use CSRF protection before production deployment.
