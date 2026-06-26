from app.services.persian_mojibake_scan_service import PersianMojibakeScanService


def test_mojibake_scan_detects_marker(tmp_path):
    path = tmp_path / "bad.html"
    path.write_text("Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯", encoding="utf-8")
    findings = PersianMojibakeScanService().scan([path])
    assert str(path) in findings
