# Inbound Privacy Redaction Policy

Inbound bodies are sanitized and truncated to configured limits. Raw email is not stored by default. Attachments are metadata-only in the MVP and are not downloaded to disk.

Secrets, authorization headers, tokens, passwords, and unnecessary raw headers must not appear in reports or dashboard views.
