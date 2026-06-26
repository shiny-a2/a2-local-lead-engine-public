class CustomerFacingBoundaryService:
    forbidden_outputs = {
        "customer_facing_quote",
        "customer_facing_proposal",
        "customer_facing_reply",
        "meeting_invite",
        "payment_link",
    }

    def assert_internal_only(self, output_type: str) -> bool:
        if output_type in self.forbidden_outputs:
            raise ValueError(f"{output_type} is forbidden in Phase 13; internal guidance only.")
        return True

    def internal_guidance(self, text: str) -> str:
        self.assert_internal_only("internal_guidance")
        return text
