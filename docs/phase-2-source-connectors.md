# Phase 2 Source Connectors

Phase 2 adds raw intake from Geoapify, OSM/Overpass, and NZBN. It stores source runs,
requests, raw records, cache entries, candidate NZBN matches, and future personalization
evidence.

This phase does not verify final website status, score leads, write emails, send emails, call
AI, call Tavily, use Google Maps/Places, or create send-ready leads.

Live execution is fail-closed. It requires `LIVE_API_CALLS_ENABLED=true`,
`LEAD_COLLECTION_ENABLED=true`, connector configuration, and budget approval. Dry-run is the
default and never calls the network.

Final verdict target:

- `PHASE_2_RAW_SOURCE_CONNECTORS_READY`
- `RAW_INTAKE_READY_FOR_PHASE_3_NORMALIZATION`

