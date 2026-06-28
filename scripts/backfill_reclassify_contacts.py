"""One-time backfill: re-classify EXISTING contacts under the widened role-mailbox rules so
leads whose only email was a role inbox (enquiries@/office@/salon@...) stop being held as
"no safe contact". Network-free, GPT-free, append-only, and guarded against wrong-business
addresses. DRY-RUN by default; pass --apply to write. Run on a COPY first to preview.

    .venv/Scripts/python.exe scripts/backfill_reclassify_contacts.py --db a2_local.db          # preview
    .venv/Scripts/python.exe scripts/backfill_reclassify_contacts.py --db a2_local.db --apply   # write
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.enums import ContactRiskLevel, Phase4Decision
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.contact_candidate import ContactCandidate
from app.db.models.phase4_candidate_decision import Phase4CandidateDecision
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.session import make_session_factory
from app.services.contact_relevance_service import ContactRelevanceService
from app.services.contact_risk_service import ContactRiskService
from app.services.contact_verification_service import ContactVerificationService
from app.services.lead_scoring_service import LeadScoringService
from app.services.web_presence_decision_service import WebPresenceDecisionService
from app.settings import Settings

CAMPAIGN = "auckland-local-website-pilot"
APPLY = "--apply" in sys.argv
DB = "a2_local.db"
for i, a in enumerate(sys.argv):
    if a == "--db" and i + 1 < len(sys.argv):
        DB = sys.argv[i + 1]


def _name_token_overlap(business_name: str, email: str) -> bool:
    stem = email.split("@")[-1].split(".")[0].lower()
    tokens = {t for t in business_name.lower().replace("&", " ").split() if len(t) >= 4}
    return any(t in stem or stem in t for t in tokens) or any(t[:5] in stem for t in tokens)


def main() -> None:
    settings = Settings(database_url=f"sqlite:///./{DB}", pipeline_skip_processed=True)
    session = make_session_factory(settings)()
    risk = ContactRiskService()
    relevance = ContactRelevanceService()

    rows = session.scalars(
        select(ContactCandidate).where(
            ContactCandidate.contact_type == "EMAIL",
            ContactCandidate.allowed_for_outreach.is_(False),
            ContactCandidate.blocked_reason == "PERSONAL_LOOKING_EMAIL",
        )
    ).all()

    touched_forbidden = 0  # tripwire: must stay 0
    flipped_rows: list[ContactCandidate] = []
    promoted_candidates: dict[int, CandidateBusiness] = {}
    skipped_wrong_business: list[str] = []

    by_candidate: dict[int, list[ContactCandidate]] = {}
    for row in rows:
        by_candidate.setdefault(row.candidate_business_id, []).append(row)

    for cand_id, contacts in by_candidate.items():
        cand = session.get(CandidateBusiness, cand_id)
        if cand is None:
            continue
        already_allowed = session.scalar(
            select(CandidateContactVerification).where(
                CandidateContactVerification.candidate_business_id == cand_id,
                CandidateContactVerification.outreach_contact_allowed.is_(True),
            )
        )
        if already_allowed:
            continue  # already sendable via some other contact; don't churn
        candidate_flips: list[ContactCandidate] = []
        for row in contacts:
            if row.blocked_reason in {"CONTACT_DOMAIN_MISMATCH", "PERSONAL_EMAIL_DOMAIN"}:
                touched_forbidden += 1  # should be impossible given the WHERE filter
                continue
            email_type, level, _ = risk.classify_email(row.contact_value, None)
            if not risk.outreach_allowed(email_type, level):
                continue
            # Wrong-business guard: no official domain here, so require a positive same-business
            # signal before this email can become the lead's outreach address.
            plausible, _why = relevance.is_plausible(cand.display_name, cand.country, row.contact_value)
            if not (plausible and _name_token_overlap(cand.display_name, row.contact_value)):
                skipped_wrong_business.append(f"{cand.display_name} -> {row.contact_value}")
                continue
            candidate_flips.append(row)
        if not candidate_flips:
            continue
        for row in candidate_flips:
            row.allowed_for_outreach = True
            row.risk_level = ContactRiskLevel.LOW
            row.requires_manual_review = False
            row.blocked_reason = None
            row.evidence_json = {**(row.evidence_json or {}), "reclassified_backfill": True, "old_blocked_reason": "PERSONAL_LOOKING_EMAIL"}
            flipped_rows.append(row)
        promoted_candidates[cand_id] = cand

    if touched_forbidden:
        print(f"TRIPWIRE TRIGGERED: touched {touched_forbidden} forbidden rows; aborting")
        session.rollback()
        sys.exit(2)

    # Append-only re-derive verification + re-open Phase4/Phase5 for promoted candidates.
    reopened5 = 0
    for cand_id in promoted_candidates:
        latest_v = session.scalar(
            select(CandidateContactVerification)
            .where(CandidateContactVerification.candidate_business_id == cand_id)
            .order_by(CandidateContactVerification.id.desc())
        )
        run_id = latest_v.verification_run_id if latest_v else None
        all_contacts = session.scalars(
            select(ContactCandidate).where(ContactCandidate.candidate_business_id == cand_id)
        ).all()
        session.flush()
        new_v = ContactVerificationService(session).summarize(cand_id, run_id, list(all_contacts))
        # Phase 4: if the lead was rejected purely on contact risk, re-decide with the new contact.
        latest4 = session.scalar(
            select(Phase4CandidateDecision)
            .where(Phase4CandidateDecision.candidate_business_id == cand_id)
            .order_by(Phase4CandidateDecision.id.desc())
        )
        if latest4 and latest4.decision == Phase4Decision.REJECT_COMPLIANCE_RISK:
            d = WebPresenceDecisionService().decide(latest4.website_status, new_v.contact_status)
            if d["decision"] == Phase4Decision.READY_FOR_PHASE_5_SCORING:
                session.add(Phase4CandidateDecision(
                    candidate_business_id=cand_id, verification_run_id=latest4.verification_run_id,
                    decision=d["decision"], decision_confidence=d["confidence"],
                    website_status=latest4.website_status, contact_status=new_v.contact_status,
                    ready_for_phase5=d["ready_for_phase5"], manual_review_required=d["manual_review_required"],
                    reject_reason=d["reject_reason"], warnings_json=["reopened_by_contact_reclassify_backfill"],
                ))
        # Phase 5: drop ONLY the no-safe-contact hold so re-scoring can re-evaluate this lead.
        for p5 in session.scalars(select(Phase5CandidateDecision).where(
            Phase5CandidateDecision.candidate_business_id == cand_id,
            Phase5CandidateDecision.decision == "HOLD_NO_SAFE_CONTACT",
        )).all():
            session.delete(p5)
            reopened5 += 1

    print(f"DB={DB}  mode={'APPLY' if APPLY else 'DRY-RUN (no write)'}")
    print(f"role-mailbox contacts flipped: {len(flipped_rows)} across {len(promoted_candidates)} candidates")
    print(f"phase5 holds reopened: {reopened5}")
    if skipped_wrong_business:
        print(f"skipped (wrong-business guard): {len(skipped_wrong_business)}")
        for s in skipped_wrong_business[:10]:
            print(f"   - {s}")
    print("newly-promoted candidates:")
    for cand in promoted_candidates.values():
        print(f"   - {cand.display_name} ({cand.city}, {cand.country})")

    if APPLY:
        session.commit()
        # Re-score the reopened leads (pipeline_skip_processed skips everyone who still has a P5 row).
        run = LeadScoringService(session, settings).score_candidates(CAMPAIGN, limit=200, commit=True)
        session.commit()
        ready = session.scalar(select(Phase5CandidateDecision.candidate_business_id).where(
            Phase5CandidateDecision.decision == "READY_FOR_PHASE_6_INSIGHT"))
        print(f"APPLIED. re-score run={run.status.value}; ready-for-phase6 now exists={bool(ready)}")
    else:
        session.rollback()
        print("DRY-RUN complete; nothing written. Re-run with --apply to commit.")
    session.close()


if __name__ == "__main__":
    main()
