# Candidate Identity Resolution Policy

Name normalization lowercases, trims whitespace, collapses duplicate spaces, normalizes
apostrophes, maps `&` to `and` for matching only, removes punctuation for matching only, and
removes legal suffixes for matching only.

Display names are preserved. Identity fingerprints are deterministic and based on normalized
name, canonical category, city, and suburb or geohash bucket.

Match scoring is explainable and uses name similarity, source ids, phone/website hints, category,
address/location proximity, and NZBN candidate hints as supporting evidence only.

Merge blockers include branch/chain risk, generic names without strong evidence, far location,
conflicting category, and NZBN mismatch.

