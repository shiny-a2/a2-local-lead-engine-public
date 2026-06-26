# Pilot Batch Selection Policy

Pilot batches select P1 first, then P2. P3, P4, and P5 candidates are never selected.

Batch creation is idempotent by `batch_name + candidate_business_id`. The batch is only an input list for Phase 6 insight/offer generation and must not create email drafts or sends.

When enough candidates exist, category and suburb diversity caps should prevent a batch from being dominated by one segment.
