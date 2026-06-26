from email.message import EmailMessage

from app.core.enums import ProviderStatus
from app.services.cpanel_smtp_provider import CpanelSmtpProvider
from app.settings import Settings
from tests.phase10_helpers import send_settings


def test_missing_smtp_config_blocks():
    ok, gaps = CpanelSmtpProvider(Settings()).check_config()
    assert ok is False
    assert "SMTP_HOST_MISSING" in gaps


def test_mocked_smtp_accepted_maps_to_sent_to_provider():
    class SMTP:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def starttls(self): self.tls = True
        def login(self, *_): pass
        def send_message(self, _): return {}

    msg = EmailMessage()
    msg["Message-ID"] = "x"
    result = CpanelSmtpProvider(send_settings(), SMTP).send(msg, dry_run=False)
    assert result.provider_status == ProviderStatus.ACCEPTED
