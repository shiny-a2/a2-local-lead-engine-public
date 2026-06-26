from app.core.enums import EmailJudgeFindingType
from app.services.email_rule_judge_service import EmailRuleJudgeService
from app.settings import Settings
from tests.phase8_helpers import allowed_claim, draft, evidence, passing_precheck


def test_all_claims_have_evidence():
    result, _ = EmailRuleJudgeService().judge(1, draft(), evidence(), allowed_claim(), passing_precheck(), Settings())
    assert result.evidence_alignment_passed is True


def test_evidence_mapping_missing_blocked():
    result, findings = EmailRuleJudgeService().judge(1, draft(), [], allowed_claim(), passing_precheck(), Settings())
    assert result.passed is False
    assert any(item["finding_type"] == EmailJudgeFindingType.EVIDENCE_MAPPING_MISSING.value for item in findings)


def test_claim_permission_missing_warns():
    result, findings = EmailRuleJudgeService().judge(1, draft(), evidence(), [], passing_precheck(), Settings())
    assert result.passed is True
    assert any(item["finding_type"] == EmailJudgeFindingType.UNSUPPORTED_CLAIM.value for item in findings)
