import pytest

from app.services.human_only_action_guard_service import HumanOnlyActionGuardService
from app.settings import Settings


def test_auto_reply_blocked():
    assert not HumanOnlyActionGuardService(Settings(testing=True)).check("auto_reply").allowed


def test_auto_quote_blocked():
    assert not HumanOnlyActionGuardService(Settings(testing=True)).check("auto_quote").allowed


def test_auto_meeting_blocked():
    assert not HumanOnlyActionGuardService(Settings(testing=True)).check("auto_meeting").allowed


def test_auto_proposal_blocked():
    assert not HumanOnlyActionGuardService(Settings(testing=True)).check("auto_proposal").allowed


def test_payment_link_blocked():
    assert not HumanOnlyActionGuardService(Settings(testing=True)).check("payment_link").allowed


def test_auto_call_blocked():
    with pytest.raises(ValueError):
        HumanOnlyActionGuardService(Settings(testing=True)).assert_allowed("auto_call")
