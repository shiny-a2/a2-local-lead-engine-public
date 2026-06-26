from app.services.backup_export_service import BackupExportService


def test_backup_export_manifest_excludes_secrets(session, tmp_path):
    row = BackupExportService(session).record_manifest(None, tmp_path)
    assert row.secrets_included is False
    assert ".env files" in tmp_path.joinpath("phase14-export-manifest.txt").read_text()
