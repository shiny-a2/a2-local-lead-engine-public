from app.db.models.scoring_profile_snapshot import ScoringProfileSnapshot

SCORING_PROFILE = "auckland_mvp_email_only_v1"
SCORE_VERSION = "v1.0"


class ScoringProfileService:
    def formula(self) -> dict[str, object]:
        return {
            "overall": {
                "website_opportunity_score": 0.30,
                "business_fit_score": 0.20,
                "contact_readiness_score": 0.20,
                "personalization_potential_score": 0.20,
                "compliance_safety_score": 0.10,
                "risk_penalty": -1,
            },
            "profile": SCORING_PROFILE,
            "version": SCORE_VERSION,
        }

    def gate_policy(self) -> dict[str, object]:
        return {
            "blocker_gates_override_score": True,
            "ready_for_phase6_only": True,
            "no_send_permission": True,
        }

    def campaign_lane_policy(self) -> dict[str, object]:
        return {
            "mvp_lanes": ["NO_WEBSITE", "SOCIAL_ONLY", "DIRECTORY_ONLY"],
            "weak_website": "hold_for_future_campaign",
            "strong_website": "reject_for_no_website_mvp",
        }

    def snapshot(self, scoring_run_id: int) -> ScoringProfileSnapshot:
        return ScoringProfileSnapshot(
            scoring_run_id=scoring_run_id,
            scoring_profile=SCORING_PROFILE,
            score_version=SCORE_VERSION,
            formula_json=self.formula(),
            gate_policy_json=self.gate_policy(),
            campaign_lane_policy_json=self.campaign_lane_policy(),
        )
