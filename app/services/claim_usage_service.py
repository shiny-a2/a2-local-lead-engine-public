from app.core.enums import EmailClaimRiskLevel
from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_generation_input import EmailGenerationInput


class ClaimUsageService:
    def usages(self, draft_id: int, body: str, generation_input: EmailGenerationInput) -> list[EmailDraftClaimUsage]:
        rows: list[EmailDraftClaimUsage] = []
        for claim in generation_input.allowed_claims_json:
            if claim and claim.lower() in body.lower():
                rows.append(
                    EmailDraftClaimUsage(
                        email_draft_variant_id=draft_id,
                        claim_type="allowed_offer_claim",
                        claim_text=claim,
                        allowed=True,
                        risk_level=EmailClaimRiskLevel.LOW,
                        reason="Listed in allowed claims from Phase 6 input.",
                    )
                )
        for claim in generation_input.blocked_claims_json:
            if claim and claim.lower() in body.lower():
                rows.append(
                    EmailDraftClaimUsage(
                        email_draft_variant_id=draft_id,
                        claim_type="blocked_offer_claim",
                        claim_text=claim,
                        allowed=False,
                        risk_level=EmailClaimRiskLevel.BLOCKED,
                        reason="Blocked in Phase 6.",
                    )
                )
        if "you don't have a website" in body.lower():
            rows.append(
                EmailDraftClaimUsage(
                    email_draft_variant_id=draft_id,
                    claim_type="absolute_no_website_claim",
                    claim_text="you don't have a website",
                    allowed=False,
                    risk_level=EmailClaimRiskLevel.BLOCKED,
                    reason="Absolute no-website claim is forbidden.",
                )
            )
        return rows
