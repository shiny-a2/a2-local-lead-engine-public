# Scoring Formula Policy

Default profile: `auckland_mvp_email_only_v1`

Score version: `v1.0`

Formula:

`overall = website_opportunity * 0.30 + business_fit * 0.20 + contact_readiness * 0.20 + personalization_potential * 0.20 + compliance_safety * 0.10 - risk_penalty`

The score is an internal prioritization score, not a promise of reply probability and not permission to send.

Every run stores a scoring profile snapshot so later formula changes do not reinterpret old scores.
