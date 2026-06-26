def test_phase14_no_outbound_terms_in_service_names():
    forbidden = ["send_email", "smtp", "openai", "collect_leads", "sync_inbox"]
    service_names = [
        "PilotFunnelAnalyticsService",
        "FinalPilotReportService",
        "MVPClosureGateService",
    ]
    assert all(term not in " ".join(service_names).lower() for term in forbidden)
