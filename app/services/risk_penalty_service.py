from app.db.models.candidate_business import CandidateBusiness


class RiskPenaltyService:
    def calculate(self, candidate: CandidateBusiness, warnings: list[str]) -> tuple[float, list[str]]:
        flags: list[str] = []
        penalty = 0.0
        if candidate.chain_risk_score >= 50:
            penalty += 25
            flags.append("chain_or_branch_risk")
        if candidate.generic_name_risk_score >= 60:
            penalty += 15
            flags.append("generic_name_risk")
        if candidate.duplicate_risk_score >= 50:
            penalty += 15
            flags.append("duplicate_risk")
        if warnings:
            penalty += min(20, len(warnings) * 5)
            flags.extend(warnings)
        return penalty, flags
