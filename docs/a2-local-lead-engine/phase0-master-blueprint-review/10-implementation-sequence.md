# Implementation Sequence

1. Resolve Phase 0 critical decisions or explicitly defer non-blocking items.
2. Implement Phase 1 foundation and safety gates.
3. Run tests, migrations, safety report, and stop for review.
4. Implement Phase 2 source intake in dry-run first; live source calls only after flags and budgets.
5. Implement Phase 3 candidate normalization; stop if dedupe/quality is weak.
6. Implement Phase 4 verification; stop if evidence/claim permissions are not reliable.
7. Implement Phase 5 scoring and pilot selection; stop if personalization/contact quality is weak.
8. Implement Phase 6 offer matching; stop if category playbooks or claim safety are missing.
9. Implement Phase 7 drafting only after AI flags/model are configured; dry-run never calls OpenAI.
10. Implement Phase 8 judge; rule judge always runs.
11. Implement Phase 9 human review dashboard; no sending.
12. Implement Phase 10 controlled sending; first live send only after provider, unsubscribe, suppression, limits, and kill switch review.
13. Implement Phase 11 inbox/bounce; no outbound replies.
14. Implement Phase 12/13 manual sales planning; no sales automation.
15. Implement Phase 14 governance and scale decision; stop before Phase 15.
16. Implement Phase 15 only after country-specific approval.

After each phase return:
- files changed
- migrations
- commands run
- tests
- reports
- safety summary
- final verdict
- gaps/manual decisions

Stop and review after Phases 1, 4, 5, 8, 10, 11, 14, and before Phase 15.
