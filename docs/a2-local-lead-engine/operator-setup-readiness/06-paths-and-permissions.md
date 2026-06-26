# 06 - Paths And Permissions

## Probe Results

| Path | Status |
|---|---|
| `reports/` | writable |
| `exports/` | writable |
| `logs/` | writable |

The probe created and removed a temporary `.operator-write-check` file in each path.

## Secret Handling

- `.env` is missing and was not exported.
- `config check` redacted secret values as `PRESENT` or `MISSING`.
- A static scan of `reports` and `docs` did not find raw secret-like values; the only hit was documentation text containing a report filename pattern with `sk` inside `risk-register`.

## Recommended Server Paths

On Alphacore, keep writable paths private:

```text
/opt/a2-local-lead-engine/reports
/opt/a2-local-lead-engine/exports
/opt/a2-local-lead-engine/logs
```

Do not place `.env` inside `reports` or `exports`.
