# Phase 3 Normalization & Dedupe

Goal: convert `raw_source_records` into clean `candidate_businesses` with provenance,
aliases, normalized locations/categories, data quality, duplicate clusters, manual review
items, conflicts, and safe future-copy evidence.

In scope: local normalization, dedupe planning, candidate quality/readiness for Phase 4,
manual review reports, and read-only API views.

Out of scope: website verification, Tavily, OpenAI, email writing, email sending, outreach,
Google Maps/Places, voice calls, and sales lead scoring.

Flow: raw records remain immutable. Normalization runs read raw records, create candidates,
link sources, preserve aliases, consolidate evidence, and create reports.

CLI:

- `python -m app.cli.main normalize run --campaign ... --source-run ... --dry-run`
- `python -m app.cli.main normalize run --campaign ... --source-run ... --commit`
- `python -m app.cli.main dedupe run --campaign ... --dry-run`
- `python -m app.cli.main quality candidates --campaign ... --commit`
- `python -m app.cli.main evidence consolidate --campaign ... --commit`
- `python -m app.cli.main report candidates --campaign ...`
- `python -m app.cli.main report manual-review --campaign ...`

Acceptance requires tests passing, reports generated, no external calls, and no outreach.

