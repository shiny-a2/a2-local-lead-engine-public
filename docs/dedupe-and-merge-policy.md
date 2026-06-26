# Dedupe And Merge Policy

Auto merge is allowed only for high-confidence, non-risky matches. Manual review is required for
ambiguous matches. Branch, chain, and multi-location clusters are not auto-merged.

Duplicate clusters store raw ids, reasons, scores, and risk flags. Rebuild behavior must be
explicit and must not overwrite raw source records.

