# Bounce Processing Policy

Phase 11 detects hard, soft, and unknown bounces from inbound DSN-like messages or provider events. Hard bounces may be suppressed when `AUTO_SUPPRESS_HARD_BOUNCES=true`. Unknown bounces require manual review.

cPanel bounce handling remains mailbox/manual-review oriented unless a later phase adds robust IMAP parsing or provider webhooks.
