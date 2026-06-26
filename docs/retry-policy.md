# Retry Policy

Retries are limited by `SEND_MAX_RETRIES`. Transient errors may be retried; permanent and provider config/auth errors should not be retried indefinitely.
