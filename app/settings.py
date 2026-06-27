import os
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.redaction import redact_mapping, secret_presence

# Operator config lives in `.env`. The test suite points A2_ENV_FILE at a non-existent
# file so operator values (sender identity, SMTP, OpenAI key) never leak into tests that
# assert safe defaults.
_ENV_FILE = os.environ.get("A2_ENV_FILE", ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    app_name: str = "A2 Local Lead Engine"
    app_timezone: str = "UTC"
    public_base_url: str = "https://amiraliyaghouti.com"
    unsubscribe_base_url: str = "https://amiraliyaghouti.com/unsubscribe"
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/a2_leads"
    log_level: str = "INFO"
    audit_log_enabled: bool = True
    local_api_only: bool = True
    live_api_calls_enabled: bool = False
    lead_collection_enabled: bool = False
    ai_generation_enabled: bool = False
    email_drafting_enabled: bool = False
    email_sending_enabled: bool = False
    followup_enabled: bool = False
    voice_calls_enabled: bool = False
    google_maps_enabled: bool = False
    public_dashboard_enabled: bool = False
    geoapify_api_key: str = ""
    tavily_api_key: str = ""
    website_verification_enabled: bool = False
    contact_verification_enabled: bool = False
    contact_discovery_enabled: bool = False
    contact_discovery_max_results: int = 5
    nzbn_api_key: str = ""
    openai_api_key: str = ""
    openai_email_model: str = ""
    openai_email_temperature: float = 0.4
    openai_email_max_tokens: int = 900
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Amirali Yaghouti"
    smtp_reply_to: str = ""
    max_daily_email_sends: int = 10
    max_api_calls_per_run: int = 100
    max_leads_per_run: int = 100
    require_manual_approval: bool = True
    data_retention_days: int = 365
    audit_retention_days: int = 730
    geoapify_daily_credit_budget: int = 500
    geoapify_max_requests_per_run: int = 20
    osm_max_requests_per_run: int = 5
    osm_min_seconds_between_requests: int = 5
    osm_timeout_seconds: int = 60
    nzbn_max_requests_per_run: int = 50
    nzbn_min_seconds_between_requests: int = 1
    source_cache_enabled: bool = True
    source_cache_ttl_days: int = 7
    phase2_max_raw_records_per_run: int = 150
    phase2_enable_personalization_evidence: bool = True
    tavily_max_queries_per_run: int = 100
    tavily_max_queries_per_candidate: int = 5
    tavily_daily_query_budget: int = 300
    url_probe_enabled: bool = True
    url_probe_max_urls_per_candidate: int = 5
    url_probe_timeout_seconds: int = 8
    url_probe_max_bytes: int = 250000
    url_probe_user_agent: str = "A2LocalLeadEngine/phase4-verification"
    phase4_max_candidates_per_run: int = 50
    phase4_require_candidate_ready: bool = True
    phase4_verification_ttl_days: int = 45
    phase4_enable_contact_extraction: bool = True
    phase4_enable_weak_website_classification: bool = True
    phase4_enable_claim_permission_matrix: bool = True
    phase4_live_url_probe: bool = False
    email_generation_max_candidates_per_run: int = 25
    email_generation_max_variants_per_candidate: int = 2
    email_max_words: int = 140
    email_min_words: int = 70
    email_max_subject_words: int = 8
    email_min_personalization_anchors: int = 2
    email_require_json_output: bool = True
    email_local_writer_enabled: bool = False
    email_similarity_check_enabled: bool = True
    email_max_similarity_score: float = 0.82
    email_include_unsubscribe_placeholder: bool = True
    email_unsubscribe_placeholder: str = "{{unsubscribe_url}}"
    email_judge_enabled: bool = False
    email_ai_judge_enabled: bool = False
    email_judge_mode: str = "RULE_ONLY"
    email_relevance_agent_enabled: bool = False
    email_relevance_min_score: int = 70
    openai_judge_model: str = ""
    openai_judge_temperature: float = 0.0
    openai_judge_max_tokens: int = 1000
    email_judge_max_drafts_per_run: int = 50
    email_judge_min_quality_score: int = 80
    email_judge_min_truthfulness_score: int = 90
    email_judge_min_evidence_alignment_score: int = 90
    email_judge_min_personalization_score: int = 70
    email_judge_min_human_likeness_score: int = 70
    email_judge_min_non_promotional_score: int = 80
    email_judge_min_economic_claim_safety_score: int = 90
    email_judge_min_compliance_readiness_score: int = 85
    email_judge_max_spam_risk_score: int = 30
    email_judge_block_on_unsupported_claim: bool = True
    email_judge_block_on_creepy_evidence: bool = True
    email_judge_block_on_absolute_no_website: bool = True
    email_judge_block_on_commission_claim: bool = True
    email_judge_block_on_google_maps_reference: bool = True
    email_judge_block_on_missing_unsubscribe: bool = True
    email_judge_block_on_missing_sender_identity: bool = True
    email_judge_block_on_multiple_cta: bool = True
    phase9_review_dashboard_enabled: bool = False
    phase9_review_dashboard_local_only: bool = True
    phase9_basic_auth_enabled: bool = True
    phase9_review_username: str = ""
    phase9_review_password_hash: str = ""
    phase9_max_queue_items_per_run: int = 100
    phase9_review_lock_ttl_minutes: int = 30
    phase9_major_edit_percent_threshold: int = 25
    phase9_minor_edit_percent_threshold: int = 10
    phase9_require_final_pre_send_check: bool = True
    phase9_require_suppression_check: bool = True
    phase9_require_contact_finalization: bool = True
    phase9_require_sender_identity: bool = True
    phase9_require_unsubscribe_placeholder: bool = True
    default_sender_profile_slug: str = "amirali_domain_default"
    default_from_email: str = ""
    default_from_name: str = "Amirali Yaghouti"
    default_reply_to_email: str = ""
    mailbox_readiness_enabled: bool = True
    mailbox_reply_to_email: str = ""
    mailbox_monitoring_mode: str = "planned_only"
    bounce_processing_mode: str = "planned_only"
    global_outreach_kill_switch: bool = True
    country_compliance_enforced: bool = False
    controlled_send_enabled: bool = False
    provider_send_enabled: bool = False
    email_provider: str = "cpanel_smtp"
    email_provider_slug: str = "amirali_cpanel_default"
    smtp_use_tls: bool = True
    send_warmup_mode: bool = True
    send_warmup_stage: str = "starter"
    send_daily_limit: int = 10
    send_per_run_limit: int = 5
    send_per_domain_daily_limit: int = 1
    send_cooldown_days: int = 90
    target_timezone: str = "Pacific/Auckland"
    send_window_enabled: bool = True
    send_window_start: str = "09:00"
    send_window_end: str = "16:30"
    send_allowed_days: str = "Mon,Tue,Wed,Thu"
    send_window_outside_policy: str = "block"
    unsubscribe_public_base_url: str = "https://amiraliyaghouti.com/unsubscribe"
    unsubscribe_token_secret: str = ""
    # Advertise RFC 8058 one-click POST only once the public unsubscribe endpoint is deployed;
    # until then the working opt-out is the mailto/reply path.
    unsubscribe_one_click_enabled: bool = False
    delivery_events_enabled: bool = False
    bounce_webhooks_enabled: bool = False
    cpanel_bounce_mode: str = "manual_inbox_review"
    provider_circuit_breaker_enabled: bool = True
    provider_max_consecutive_failures: int = 3
    send_max_retries: int = 1
    send_retry_transient_errors_only: bool = True
    phase10_send_dashboard_enabled: bool = True
    phase10_dashboard_rtl: bool = True
    phase10_dashboard_language: str = "fa"
    email_plain_text_only: bool = True
    email_disable_tracking_pixel: bool = True
    email_disable_click_tracking: bool = True
    email_disable_attachments: bool = True
    email_disable_html: bool = True
    inbox_sync_enabled: bool = False
    imap_sync_enabled: bool = False
    provider_webhook_events_enabled: bool = False
    imap_host: str = ""
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    imap_use_ssl: bool = True
    imap_mailbox: str = "INBOX"
    imap_mark_read: bool = False
    imap_delete_messages: bool = False
    imap_move_processed: bool = False
    inbox_sync_max_messages_per_run: int = 50
    inbox_sync_since_days: int = 30
    inbound_max_body_chars: int = 20000
    inbound_store_attachments: bool = False
    inbound_attachment_metadata_only: bool = True
    inbound_store_raw_email: bool = False
    reply_classification_enabled: bool = True
    ai_reply_classification_enabled: bool = False
    openai_reply_classifier_model: str = ""
    bounce_processing_enabled: bool = True
    auto_suppress_hard_bounces: bool = True
    auto_suppress_unsubscribe_requests: bool = True
    auto_suppress_negative_replies: bool = False
    phase11_create_human_tasks: bool = True
    phase11_dashboard_language: str = "fa"
    phase11_dashboard_rtl: bool = True
    phase12_opportunity_planner_enabled: bool = True
    phase12_dashboard_language: str = "fa"
    phase12_dashboard_rtl: bool = True
    ai_reply_drafting_enabled: bool = False
    phase12_allow_reply_draft_suggestions: bool = False
    phase12_reply_drafts_internal_only: bool = True
    phase12_block_automatic_response_send: bool = True
    phase12_block_automatic_meeting_scheduling: bool = True
    phase12_block_automatic_price_quote: bool = True
    phase12_block_automatic_proposal_send: bool = True
    phase12_block_automatic_payment_link: bool = True
    phase12_require_human_action: bool = True
    phase12_default_task_due_hours: int = 24
    phase12_followup_default_delay_days: int = 3
    phase12_auto_close_negative_replies: bool = False
    phase13_sales_workspace_enabled: bool = True
    phase13_dashboard_language: str = "fa"
    phase13_dashboard_rtl: bool = True
    phase13_block_auto_reply: bool = True
    phase13_block_auto_followup: bool = True
    phase13_block_auto_quote: bool = True
    phase13_block_auto_meeting: bool = True
    phase13_block_auto_proposal: bool = True
    phase13_block_payment_link: bool = True
    phase13_block_auto_call: bool = True
    phase13_internal_pricing_worksheet_enabled: bool = True
    phase13_require_human_quote_approval: bool = True
    phase13_require_human_proposal_approval: bool = True
    phase13_require_close_reason: bool = True
    phase13_scope_completeness_quote_threshold: int = 70
    phase13_proposal_readiness_threshold: int = 80
    phase13_task_stale_days: int = 3
    phase14_governance_dashboard_enabled: bool = True
    phase14_dashboard_language: str = "fa"
    phase14_dashboard_rtl: bool = True
    phase14_min_sample_for_scale_decision: int = 25
    phase15_boundary_status: str = "POST_MVP_SCALE_NOT_REQUIRED_FOR_NZ_TINY_PILOT"
    testing: bool = Field(default=False, exclude=True)

    def safe_dict(self) -> dict[str, Any]:
        raw = self.model_dump(exclude={"testing"})
        return redact_mapping({key.upper(): value for key, value in raw.items()})

    def secret_status(self) -> dict[str, str]:
        return {
            "GEOAPIFY_API_KEY": secret_presence(self.geoapify_api_key),
            "TAVILY_API_KEY": secret_presence(self.tavily_api_key),
            "NZBN_API_KEY": secret_presence(self.nzbn_api_key),
            "OPENAI_API_KEY": secret_presence(self.openai_api_key),
            "SMTP_PASSWORD": secret_presence(self.smtp_password),
            "IMAP_PASSWORD": secret_presence(self.imap_password),
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
