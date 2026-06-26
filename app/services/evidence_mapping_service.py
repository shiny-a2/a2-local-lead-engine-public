from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
from app.db.models.email_generation_input import EmailGenerationInput


class EvidenceMappingService:
    def links(self, draft_id: int, generation_input: EmailGenerationInput) -> list[EmailDraftEvidenceLink]:
        links = [
            EmailDraftEvidenceLink(
                email_draft_variant_id=draft_id,
                evidence_type=item["type"],
                evidence_source_table="email_generation_inputs",
                evidence_source_id=generation_input.id,
                used_in_sentence=str(item["value"]),
                confidence=0.8,
            )
            for item in generation_input.verified_evidence_json
        ]
        for block in generation_input.offer_blocks_json:
            links.append(
                EmailDraftEvidenceLink(
                    email_draft_variant_id=draft_id,
                    evidence_type=block["type"],
                    evidence_source_table="future_email_offer_blocks",
                    evidence_source_id=block["id"],
                    used_in_sentence=block["text"],
                    confidence=0.8,
                )
            )
        return links
