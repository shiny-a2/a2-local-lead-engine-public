def test_no_outbound_symbols_in_phase13_services():
    from app.services import (
        customer_facing_boundary_service,
        human_only_action_guard_service,
        manual_followup_plan_service,
    )

    modules = [
        customer_facing_boundary_service,
        human_only_action_guard_service,
        manual_followup_plan_service,
    ]
    for module in modules:
        assert not hasattr(module, "SMTP")
        assert not hasattr(module, "send_email")
        assert not hasattr(module, "create_calendar_event")
        assert not hasattr(module, "payment_link")
        assert not hasattr(module, "voice_call")
