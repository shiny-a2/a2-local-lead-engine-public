from app.db.models.candidate_business import CandidateBusiness
from app.db.models.raw_source_record import RawSourceRecord

CHAIN_TERMS = ("franchise", "group", "branch", "limited", "ltd")


class ChainRiskService:
    def score_raw(self, records: list[RawSourceRecord]) -> tuple[float, list[str]]:
        flags: list[str] = []
        names = [record.raw_name.lower() for record in records if record.raw_name]
        suburbs = {record.raw_suburb for record in records if record.raw_suburb}
        websites = [record.raw_website for record in records if record.raw_website]
        phones = [record.raw_phone for record in records if record.raw_phone]
        if any(term in name for name in names for term in CHAIN_TERMS):
            flags.append("chain_term_in_name")
        if len(suburbs) > 1:
            flags.append("multiple_suburbs")
        if len(set(websites)) == 1 and len(websites) > 1:
            flags.append("same_website_multiple_locations")
        if len(set(phones)) == 1 and len(phones) > 2:
            flags.append("same_phone_many_locations")
        return min(100.0, len(flags) * 35.0), flags

    def score_candidate(self, candidate: CandidateBusiness) -> tuple[float, list[str]]:
        flags = []
        name = candidate.normalized_name.lower()
        if any(term in name for term in CHAIN_TERMS):
            flags.append("chain_term_in_name")
        if candidate.chain_risk_score >= 70:
            flags.append("existing_high_chain_risk")
        return min(100.0, len(flags) * 50.0), flags

