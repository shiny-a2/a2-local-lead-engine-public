# Dependency Graph

## Strict Sequential Chain

| Phase | Must Exist Before Start | Consumes | Produces For |
|---|---|---|---|
| 1 | Phase 0 decisions | infra assumptions | all phases |
| 2 | safety flags, DB, CLI, campaigns | source settings | Phase 3 |
| 3 | raw source records | Phase 2 raw tables | Phase 4 |
| 4 | candidates | Phase 3 candidates/evidence | Phase 5/6/7 claim safety |
| 5 | verified candidates | Phase 4 decisions/gates | Phase 6/pilot batch |
| 6 | Phase 5 ready candidates | scores, lanes, evidence | Phase 7 copy inputs |
| 7 | offer blocks and allowed evidence | Phase 6 outputs | Phase 8 drafts |
| 8 | draft variants | evidence maps, claims | Phase 9 human queue |
| 9 | judge-approved drafts | Phase 8 decisions | Phase 10 send queue |
| 10 | human-approved Phase 10 queue | provider/suppression/unsubscribe | Phase 11 inbound matching |
| 11 | sent snapshots/message ids | inbox/provider events | Phase 12 opportunities |
| 12 | lead response statuses | replies/classifications | Phase 13 sales workspace |
| 13 | manual opportunities | Phase 12 guidance | Phase 14 governance |
| 14 | complete pilot metrics | all MVP outputs | Phase 15 gate |
| 15 | Phase 14 scale decision | localization/country decisions | controlled expansion |

## Parallelizable Work

| Workstream | Can Start After | Notes |
|---|---|---|
| Documentation policy writing | Phase 0 | Must not claim implementation |
| Test skeletons per phase | Phase 1 | Keep tests scoped to current phase |
| Dashboard visual language | Phase 8/9 planning | Static design only before implementation |
| Provider evaluation | Phase 9 planning | No sending until Phase 10 |
| Legal/compliance research | Phase 0 | Manual review, not solved by code |

## Strictly Sequential Items
- Candidate scoring must not run before verification/claim permission.
- Email writing must not run before offer blocks and allowed claims exist.
- Sending must not run before human approval and final pre-send checks.
- Inbox/reply CRM must not run before send snapshots/message ids exist.
- Expansion must not start before pilot governance says scale is acceptable.
