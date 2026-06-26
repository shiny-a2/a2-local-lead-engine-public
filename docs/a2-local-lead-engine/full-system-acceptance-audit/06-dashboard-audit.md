# 06 - Dashboard Audit

| Dashboard | Routes found | Templates found | Persian/RTL | Auth/private access | Allowed actions | Forbidden actions absent? | Verdict |
|---|---|---|---|---|---|---|---|
| Phase 9 Review | `/admin/review` routes found | `app/templates/review/*` | Mostly English, expected Phase 9 | Dashboard disabled by default; MVP header auth | final check, edit, approve for Phase 10, hold/reject/return | No send/schedule controls found | WARNING |
| Phase 10 Send | `/admin/send`, `/unsubscribe` routes found | `app/templates/send/*` | `base_fa.html` RTL; route inline text shows mojibake | Weak: may not require auth if username blank | view queue, suppression add/import, hold/cancel | No send-all button found; no dashboard send button found | WARNING |
| Phase 11 Inbox | `/admin/inbox`, `/webhooks` routes found | `app/templates/inbox/*` | RTL exists; some mojibake | Simple Authorization/header check, no password validation | classify override, create task, suppress, close/update task | No reply/follow-up send button found | WARNING |
| Phase 12 Opportunity | `/admin/opportunities` routes found | `app/templates/opportunity/*` | RTL exists | Simple auth response when enabled | create task, close, mark manual response/call | No send price/proposal/meeting controls found | WARNING |
| Phase 13 Sales Workspace | `/admin/sales` routes found | `app/templates/sales_workspace/*` | RTL exists | Simple auth response when enabled | update scope/proposal/pricing, manual quote approval, task/log/close | No automated send/meeting/payment controls found | WARNING |
| Phase 14 Governance | None found | None found | None found | None | N/A | N/A | BLOCK |
| Phase 15 Country | None found | None found | None found | None | N/A | N/A | BLOCK |

## Security Notes

- Phase 9 `DashboardAuthService` is intentionally MVP/lightweight and says full password verification can be added once deployed.
- Phase 10 dashboard auth checks `x-review-user` only if `PHASE9_REVIEW_USERNAME` is set; with a blank username and dashboard enabled, routes are effectively not credential protected.
- Phase 11/12/13 route auth is inconsistent and not a production session/auth model.
- CSRF protection was not found as a first-class dashboard mechanism.

## UX Notes

- Persian/RTL templates exist for Phase 10-13.
- Some Persian strings appear mojibake in route-generated HTML and `inbox/mailbox_readiness.html`, which should be fixed before operator use.
- Email content is displayed in LTR blocks in some templates; full visual inspection with a running local app was not performed because the operational DB is unavailable.
