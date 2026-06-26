# Provider Abstraction Policy

Providers implement config checks, send, result normalization, and capability reporting. Initial providers are `null_dry_run`, `cpanel_smtp`, and `manual_smtp`.

Future providers can include Google Workspace, Mailgun, Amazon SES, SendGrid, and Postmark. Secrets stay in environment variables or a future secrets manager, never in DB.
