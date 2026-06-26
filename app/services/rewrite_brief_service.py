from app.db.models.email_rewrite_brief import EmailRewriteBrief


class RewriteBriefService:
    def build(self, run_id: int, draft_id: int, candidate_id: int, findings: list[dict[str, object]]) -> EmailRewriteBrief:
        must_remove = [str(item["message"]) for item in findings if item["severity"] == "BLOCKER"]
        must_soften = [str(item["message"]) for item in findings if item["severity"] == "WARNING"]
        return EmailRewriteBrief(
            email_judge_run_id=run_id,
            email_draft_variant_id=draft_id,
            candidate_business_id=candidate_id,
            rewrite_reason="Rule judge found issues; no rewritten body generated.",
            rewrite_instructions_json=["Keep the draft short, evidence-bound, and non-promotional."],
            must_keep_json=["sender identity", "unsubscribe placeholder", "safe personalization anchors"],
            must_remove_json=must_remove,
            must_soften_json=must_soften,
        )
