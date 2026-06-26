from app.services.retention_policy_service import RetentionPolicyService


def test_retention_policy_excludes_env_files(session, test_settings):
    rows = RetentionPolicyService(session, test_settings).create()
    assert any(row.policy_name == "exports" and row.notes_json["exclude_env_files"] for row in rows)
