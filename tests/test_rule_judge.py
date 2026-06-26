from app.core.enums import EmailJudgeFindingType
from app.services.email_rule_judge_service import EmailRuleJudgeService
from app.settings import Settings
from tests.phase8_helpers import allowed_claim, draft, evidence, passing_precheck


def judge_body(body: str):
    return EmailRuleJudgeService().judge(1, draft(body=body), evidence(), allowed_claim(), passing_precheck(), Settings())


def finding_types(findings):
    return {item["finding_type"] for item in findings}


def test_blocks_absolute_no_website_claim():
    _, findings = judge_body("You don't have a website. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.ABSOLUTE_NO_WEBSITE_CLAIM.value in finding_types(findings)


def test_blocks_commission_claim():
    _, findings = judge_body("Stop paying commissions. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.COMMISSION_CLAIM.value in finding_types(findings)


def test_blocks_guaranteed_savings_bookings():
    _, findings = judge_body("Guaranteed bookings can save thousands. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.GUARANTEED_RESULT_CLAIM.value in finding_types(findings)


def test_blocks_google_maps_reference():
    _, findings = judge_body("I saw you on Google Maps. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.GOOGLE_MAPS_REFERENCE.value in finding_types(findings)


def test_blocks_platform_attack_language():
    _, findings = judge_body("Social media is bad and directories are bad. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.PLATFORM_ATTACK.value in finding_types(findings)


def test_blocks_creepy_evidence():
    _, findings = judge_body("I found your owner name and NZBN. I am Amirali. {{unsubscribe_url}}?")
    assert EmailJudgeFindingType.CREEPY_EVIDENCE.value in finding_types(findings)


def test_blocks_missing_unsubscribe_and_sender_identity_and_multiple_ctas():
    _, findings = EmailRuleJudgeService().judge(
        1,
        draft(body="Would this help? Can we talk?"),
        evidence(),
        allowed_claim(),
        passing_precheck(),
        Settings(),
    )
    types = finding_types(findings)
    assert EmailJudgeFindingType.MISSING_UNSUBSCRIBE.value in types
    assert EmailJudgeFindingType.MISSING_SENDER_IDENTITY.value in types
    assert EmailJudgeFindingType.MULTIPLE_CTA.value in types


def test_passes_safe_conservative_draft():
    result, findings = EmailRuleJudgeService().judge(1, draft(), evidence(), allowed_claim(), passing_precheck(), Settings())
    assert result.passed is True
    assert findings == []
