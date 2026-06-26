# Sender Identity Readiness Policy

Phase 9 stores sender identity metadata only. It supports provider metadata such as `cpanel_smtp`, `google_workspace`, `mailgun`, `amazon_ses`, `sendgrid`, `postmark`, and `manual_placeholder`.

SMTP passwords and API keys must not be stored in the database. Phase 10 will handle provider credentials through environment variables or a secrets manager.
