# 09 - Operator Setup Checklist For Amirali

| Group | Item | Required | Current detected status | Amirali action | Safe default | Verdict |
|---|---|---:|---|---|---|---|
| A Server | Alphacore VPS access | Yes | Not checked | Confirm SSH/deploy path/process | Private only | BLOCK until confirmed |
| A Server | Python 3.11+ | Yes | Local audit used Python 3.12.13 | Confirm VPS Python/uv installed | 3.11+ | WARNING |
| A Server | Process manager | Yes | Not checked | Decide systemd/supervisor/manual CLI | No public worker | WARNING |
| B Database | Operational DB URL | Yes | `doctor` DB `OperationalError` | Configure real local/private Postgres URL | No live commands | BLOCK |
| B Database | Migrations applied | Yes | Not verified | Run `db upgrade` after backup | Dry-run/audit first | BLOCK |
| C Domain/cPanel | Domain/subdomain | Yes for unsubscribe/dashboard | `amiraliyaghouti.com` placeholders | Confirm unsubscribe URL and any private dashboard host | Keep dashboard private | BLOCK |
| D Email sender | From/reply-to | Yes before send | Empty | Choose `hello@...` or `amirali@...` | Empty blocks send | BLOCK for live |
| D Email sender | SMTP host/user/password | Yes for cPanel send | Missing | Fill env only; never DB | Missing blocks send | BLOCK for live |
| E DNS | SPF/DKIM/DMARC | Yes before live send | Unknown | Configure and manually verify | Unknown blocks/warns | BLOCK for live |
| F Unsubscribe | Public unsubscribe URL | Yes | Placeholder present | Confirm HTTPS route/domain | Required | BLOCK for live |
| F Unsubscribe | Token secret | Yes | Missing | Generate strong secret in env | Missing unsafe for live | BLOCK for live |
| G OpenAI | API key/model | Required for live draft generation if AI used | Missing | Configure only when ready; dry-run first | Disabled | WARNING |
| H Sources | Geoapify/Tavily/NZBN keys | Needed for live intake/enrichment | Missing | Add only after source plan approval | Disabled | WARNING |
| I Campaign | Country/city/category | Yes | Seed defaults Auckland/NZ found | Confirm first pilot scope | Tiny Auckland category | BLOCK until chosen |
| J Dashboard | Credentials | Yes for hosted dashboards | username/password hash missing | Set credentials and access policy | Private/local only | BLOCK |
| K Backup | DB backup path | Yes | Not checked | Define backup and report retention paths | No live mutation | BLOCK before commit/live |
| L Legal/compliance | Manual review | Yes | Not recorded | Confirm B2B email/legal boundaries, suppression, retention | No live sending | BLOCK for live |
| M Volume | First pilot limits | Yes | Defaults: daily 10, per-run 5, per-domain 1 | Recommend first live 1-3 emails only | low-volume | WARNING |
| N Safety | Kill switch confirmation | Yes | Kill switch true | Keep true through all dry-runs; disable only immediately before tiny live send | true | PASS |

## Minimum Operator Setup Before Any Controlled Dry-Run

1. Working database and migrations.
2. Campaign seed confirmed.
3. Dashboard credentials decided if dashboards are opened.
4. Reports/log paths confirmed.
5. Source/API keys can remain missing for non-live dry-run plans.

## Minimum Operator Setup Before Any Live Send

1. All dry-run reports reviewed.
2. Phase 14 governance fixed or explicitly deferred with manual governance workaround.
3. Sender identity, cPanel SMTP env, SPF/DKIM/DMARC, reply-to, unsubscribe secret and URL configured.
4. Suppression list initialized.
5. Legal/compliance manual approval recorded.
6. Kill switch disabled only for tiny live window, with `EMAIL_SENDING_ENABLED=true`, `CONTROLLED_SEND_ENABLED=true`, `PROVIDER_SEND_ENABLED=true`.
