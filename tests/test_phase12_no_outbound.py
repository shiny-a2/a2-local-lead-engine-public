def test_no_outbound_symbols_in_phase12_services():
    from app.services import opportunity_service, pricing_guidance_service

    assert not hasattr(opportunity_service, "SMTP")
    assert not hasattr(pricing_guidance_service, "send")


def test_forbidden_statuses_not_present():
    from app.core.enums import Phase12DecisionValue

    forbidden = {"REPLY_SENT", "FOLLOWUP_SENT", "MEETING_SCHEDULED", "QUOTE_SENT"}
    assert forbidden.isdisjoint({item.value for item in Phase12DecisionValue})
