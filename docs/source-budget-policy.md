# Source Budget Policy

- Geoapify default daily credit budget: 500.
- Geoapify default max requests per run: 20.
- OSM/Overpass default max requests per run: 5.
- OSM/Overpass must stay bounded by city, category, and limit.
- NZBN default max requests per run: 50.
- Phase 2 max raw records per run: 150.
- Source cache is enabled by default.

Budget failures block runs before live requests are attempted.

