# IMAP Sync Policy

IMAP sync is disabled by default. Commit sync requires `INBOX_SYNC_ENABLED=true` and `IMAP_SYNC_ENABLED=true`.

The sync uses UID/checkpoint data, imports only new messages, and deduplicates by message-id/body hash. It does not delete messages, does not mark messages read by default, and does not move processed messages by default.
