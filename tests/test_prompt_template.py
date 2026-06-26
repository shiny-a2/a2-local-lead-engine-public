from app.services.prompt_template_service import PromptTemplateService


def test_template_rules_and_snapshot(session):
    service = PromptTemplateService(session)
    service.seed_defaults()
    template = service.choose("NO_WEBSITE", "barber")
    assert "untrusted context" in template.system_prompt
    assert "Do not invent" in template.system_prompt
    assert "blocked_claims" in template.user_prompt_template
    assert template.output_schema_json["required"] == ["drafts"]
