import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from sqlalchemy import select, text

from app.cli.sales_workspace import report_sales_workspace, sales_workspace_app
from app.core.enums import SensitiveOperation, VerificationRunOperation
from app.core.run_context import RunContext
from app.db.session import make_session_factory
from app.settings import get_settings

console = Console()
app = typer.Typer(no_args_is_help=True)
db_app = typer.Typer(no_args_is_help=True)
config_app = typer.Typer(no_args_is_help=True)
campaign_app = typer.Typer(no_args_is_help=True)
safety_app = typer.Typer(no_args_is_help=True)
report_app = typer.Typer(no_args_is_help=True)
fixtures_app = typer.Typer(no_args_is_help=True)
sources_app = typer.Typer(no_args_is_help=True)
collect_app = typer.Typer(no_args_is_help=True)
enrich_app = typer.Typer(no_args_is_help=True)
normalize_app = typer.Typer(no_args_is_help=True)
dedupe_app = typer.Typer(no_args_is_help=True)
quality_app = typer.Typer(no_args_is_help=True)
evidence_app = typer.Typer(no_args_is_help=True)
verify_app = typer.Typer(no_args_is_help=True)
score_app = typer.Typer(no_args_is_help=True)
pilot_app = typer.Typer(no_args_is_help=True)
ops_app = typer.Typer(no_args_is_help=True)
insight_app = typer.Typer(no_args_is_help=True)
offer_app = typer.Typer(no_args_is_help=True)
email_app = typer.Typer(no_args_is_help=True)
judge_app = typer.Typer(no_args_is_help=True)
review_app = typer.Typer(no_args_is_help=True)
send_app = typer.Typer(no_args_is_help=True)
inbox_app = typer.Typer(no_args_is_help=True)
opportunity_app = typer.Typer(no_args_is_help=True)
geo_app = typer.Typer(no_args_is_help=True)
improvement_app = typer.Typer(no_args_is_help=True)


def session_for_cli():
    settings = get_settings()
    return make_session_factory(settings)()


@app.command()
def doctor() -> None:
    settings = get_settings()
    checks: dict[str, str] = {
        "python": sys.version.split()[0],
        "app_env": settings.app_env,
        "audit_log_enabled": str(settings.audit_log_enabled),
        "public_base_url": "configured" if settings.public_base_url else "missing",
        "no_live_api_calls_performed": "true",
    }
    verdict = "FOUNDATION_SAFE_READY"
    try:
        with session_for_cli() as session:
            session.execute(text("select 1"))
            checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"gap: {exc.__class__.__name__}"
        verdict = "FOUNDATION_READY_WITH_GAPS"

    risky_disabled = all(
        not value
        for value in [
            settings.live_api_calls_enabled,
            settings.lead_collection_enabled,
            settings.ai_generation_enabled,
            settings.email_sending_enabled,
            settings.voice_calls_enabled,
            settings.google_maps_enabled,
            settings.public_dashboard_enabled,
        ]
    )
    checks["risky_operations_disabled"] = str(risky_disabled)
    if not risky_disabled:
        verdict = "FOUNDATION_BLOCKED"
    for key, value in checks.items():
        console.print(f"{key}: {value}")
    console.print(f"verdict: {verdict}")


@db_app.command("upgrade")
def db_upgrade() -> None:
    result = subprocess.run(["alembic", "upgrade", "head"], check=False)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)
    console.print("database migrations applied")


@config_app.command("check")
def config_check() -> None:
    settings = get_settings()
    for key, value in settings.safe_dict().items():
        console.print(f"{key}={value}")


@campaign_app.command("seed")
def campaign_seed() -> None:
    from app.services.campaign_service import seed_initial_campaign

    settings = get_settings()
    context = RunContext()
    with session_for_cli() as session:
        campaign, created = seed_initial_campaign(session, settings, context.run_id)
    console.print(
        f"campaign={campaign.slug} status={campaign.status.value} "
        f"{'created' if created else 'already_present'} run_id={context.run_id}"
    )


@safety_app.command("check")
def safety_check() -> None:
    from app.core.safety import check_all_operations

    settings = get_settings()
    for check in check_all_operations(settings):
        console.print(
            f"{check.operation}: {'ALLOWED' if check.allowed else 'BLOCKED'} "
            f"reason={check.reason} flag={check.flag} current={check.current_value}"
        )


@report_app.command("foundation")
def report_foundation() -> None:
    from app.services.report_service import build_foundation_report, write_foundation_report

    settings = get_settings()
    context = RunContext()
    with session_for_cli() as session:
        report = build_foundation_report(settings, session, context)
    md_path, json_path = write_foundation_report(report, Path("reports"))
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"verdict={report['final_verdict']}")


@fixtures_app.command("seed")
def fixtures_seed() -> None:
    from app.services.fixture_service import seed_fixture_leads

    settings = get_settings()
    context = RunContext()
    with session_for_cli() as session:
        created, skipped = seed_fixture_leads(session, settings, context.run_id)
    console.print(f"fixture_leads created={created} skipped={skipped} run_id={context.run_id}")


def _category_mapping(category: str) -> dict:
    import yaml

    path = Path("app/config/source_category_map.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if category not in data:
        raise typer.BadParameter(f"Unknown category mapping: {category}")
    return data[category]


def _commit_mode(dry_run: bool, commit: bool) -> bool:
    if commit:
        return True
    return False


@sources_app.command("list")
def sources_list() -> None:
    settings = get_settings()
    rows = [
        (
            "geoapify",
            "configured" if settings.geoapify_api_key else "missing key",
            settings.geoapify_max_requests_per_run,
        ),
        ("osm_overpass", "available no key", settings.osm_max_requests_per_run),
        (
            "nzbn",
            "configured" if settings.nzbn_api_key else "missing key",
            settings.nzbn_max_requests_per_run,
        ),
    ]
    for name, status, budget in rows:
        enabled = settings.live_api_calls_enabled and settings.lead_collection_enabled
        console.print(f"{name}: {status}, enabled={enabled}, max_requests_per_run={budget}")


@sources_app.command("check")
def sources_check() -> None:
    from app.connectors.geoapify import GeoapifyPlacesConnector
    from app.connectors.nzbn import NzbnConnector
    from app.connectors.osm_overpass import OsmOverpassConnector

    settings = get_settings()
    for connector in [
        GeoapifyPlacesConnector(settings),
        OsmOverpassConnector(settings),
        NzbnConnector(settings),
    ]:
        check = connector.check_config()
        console.print(f"{connector.source_name.value}: ready={check.ready} reason={check.reason}")
    console.print("network_check=not-called")


def _store_source_request(session, source_run, connector, request, cache_hit=False) -> None:
    from app.core.redaction import redact_mapping
    from app.db.models.source_request import SourceRequest

    session.add(
        SourceRequest(
            source_run_id=source_run.id,
            source_name=connector.source_name,
            request_key=request.request_key,
            request_url_redacted=request.url,
            request_params_json=redact_mapping(request.params),
            response_status=200 if cache_hit else None,
            cache_hit=cache_hit,
        )
    )
    session.commit()


def _run_collect(connector, params: dict, campaign: str, dry_run: bool, commit: bool) -> None:
    from app.core.enums import SourceOperation, SourceRunStatus
    from app.core.safety import check_operation
    from app.db.models.source_request import SourceRequest
    from app.services.personalization_evidence_service import PersonalizationEvidenceService
    from app.services.raw_record_service import RawRecordService
    from app.services.source_budget_service import SourceBudgetService
    from app.services.source_cache_service import SourceCacheService
    from app.services.source_quality_service import SourceQualityService, write_source_report
    from app.services.source_run_service import SourceRunService

    settings = get_settings()
    live = _commit_mode(dry_run, commit)
    operation = (
        SourceOperation.COLLECT_OSM
        if connector.source_name.value == "osm_overpass"
        else SourceOperation.COLLECT_PLACES
    )
    with session_for_cli() as session:
        run_service = SourceRunService(session)
        source_run = run_service.start(
            source_name=connector.source_name,
            operation=operation,
            dry_run=not live,
            campaign_slug=campaign,
            category=params.get("category"),
            city=params.get("city"),
            country=params.get("country"),
            requested_limit=params.get("limit"),
            metadata={"credit_estimate": connector.estimate_cost_or_credits(params)},
        )
        budget = SourceBudgetService(settings).check(
            connector.source_name, limit=int(params["limit"]), request_count=1
        )
        request = connector.build_request(params)
        _store_source_request(session, source_run, connector, request)
        if not budget.allowed:
            run_service.finish(source_run, SourceRunStatus.BLOCKED_BY_SOURCE_BUDGET)
        elif live and (
            not check_operation(settings, SensitiveOperation.LIVE_API_CALL).allowed
            or not check_operation(settings, SensitiveOperation.LEAD_COLLECTION).allowed
        ):
            run_service.finish(source_run, SourceRunStatus.BLOCKED_BY_SAFETY)
        elif live and not connector.check_config().ready:
            run_service.finish(source_run, SourceRunStatus.BLOCKED_BY_CONFIG)
        elif not live:
            run_service.finish(source_run, SourceRunStatus.DRY_RUN_ONLY)
        else:
            cache = SourceCacheService(session)
            cache_key = cache.make_cache_key(connector.source_name, request.params)
            cached = cache.get(cache_key) if settings.source_cache_enabled else None
            response = cached if cached is not None else connector.execute(request, dry_run=False)
            session.add(
                SourceRequest(
                    source_run_id=source_run.id,
                    source_name=connector.source_name,
                    request_key=request.request_key,
                    request_url_redacted=request.url,
                    request_params_json=request.params,
                    response_count=len(response.get("features", response.get("elements", []))),
                    cache_hit=cached is not None,
                )
            )
            records = connector.extract_raw_records(response)
            raw_records, skipped = RawRecordService(session).store_records(source_run, records)
            evidence_service = PersonalizationEvidenceService(session)
            for raw in raw_records:
                evidence_service.create_for_record(
                    raw,
                    connector.extract_personalization_evidence(
                        {
                            "raw_name": raw.raw_name,
                            "raw_category": raw.raw_category,
                            "raw_suburb": raw.raw_suburb,
                            "raw_city": raw.raw_city,
                            "raw_website": raw.raw_website,
                            "raw_phone": raw.raw_phone,
                            "raw_email": raw.raw_email,
                            "raw_opening_hours_json": raw.raw_opening_hours_json,
                        }
                    ),
                )
            run_service.finish(
                source_run,
                SourceRunStatus.COMPLETED,
                fetched=len(records),
                stored=len(raw_records) - skipped,
                skipped=skipped,
            )
        summary = SourceQualityService(session).build_source_run_summary(source_run)
        md_path, json_path = write_source_report(summary, Path("reports"), "source-run")
    console.print(f"source_run_id={source_run.run_id}")
    console.print(f"report={md_path}")
    console.print(f"json={json_path}")
    console.print(f"status={source_run.status.value}")


@collect_app.command("geoapify")
def collect_geoapify(
    campaign: Annotated[str, typer.Option()],
    city: Annotated[str, typer.Option()],
    country: Annotated[str, typer.Option()] = "New Zealand",
    category: Annotated[str, typer.Option()] = "barber",
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.connectors.geoapify import GeoapifyPlacesConnector

    mapping = _category_mapping(category)
    params = {
        "city": city,
        "country": country,
        "category": category,
        "source_category": mapping["geoapify"]["categories"][0],
        "limit": limit,
    }
    _run_collect(GeoapifyPlacesConnector(get_settings()), params, campaign, dry_run, commit)


@collect_app.command("osm")
def collect_osm(
    campaign: Annotated[str, typer.Option()],
    city: Annotated[str, typer.Option()],
    country: Annotated[str, typer.Option()] = "New Zealand",
    category: Annotated[str, typer.Option()] = "barber",
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.connectors.osm_overpass import OsmOverpassConnector
    from app.services.geography_service import GeographyService

    mapping = _category_mapping(category)
    tag_key, tag_values = next(iter(mapping["osm"]["tags"].items()))
    info = GeographyService().country(country)
    params = {
        "city": city,
        "country": country,
        "country_code": info.get("code", "") if info else "",
        "category": category,
        "osm_tag_key": tag_key,
        "osm_tag_values": tag_values,
        "limit": limit,
    }
    _run_collect(OsmOverpassConnector(get_settings()), params, campaign, dry_run, commit)


@enrich_app.command("nzbn")
def enrich_nzbn(
    source_run: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.connectors.nzbn import NzbnConnector
    from app.core.enums import SourceName, SourceOperation, SourceRunStatus
    from app.db.models.raw_source_record import RawSourceRecord
    from app.db.models.source_run import SourceRun
    from app.services.source_budget_service import SourceBudgetService
    from app.services.source_run_service import SourceRunService

    settings = get_settings()
    connector = NzbnConnector(settings)
    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        parent = session.scalar(select(SourceRun).where(SourceRun.run_id == source_run))
        run = SourceRunService(session).start(
            source_name=SourceName.NZBN,
            operation=SourceOperation.ENRICH_NZBN,
            dry_run=not live,
            requested_limit=limit,
            metadata={"parent_source_run": source_run},
        )
        records = session.scalars(
            select(RawSourceRecord).where(RawSourceRecord.source_run_id == parent.id).limit(limit)
        ).all() if parent else []
        budget = SourceBudgetService(settings).check(
            SourceName.NZBN, limit=limit, request_count=len(records)
        )
        status = SourceRunStatus.DRY_RUN_ONLY
        if not budget.allowed:
            status = SourceRunStatus.BLOCKED_BY_SOURCE_BUDGET
        elif live and not connector.check_config().ready:
            status = SourceRunStatus.BLOCKED_BY_CONFIG
        SourceRunService(session).finish(run, status, fetched=len(records))
    console.print(f"source_run_id={run.run_id}")
    console.print(f"status={run.status.value}")


@report_app.command("source-run")
def report_source_run(run_id: str) -> None:
    from app.db.models.source_run import SourceRun
    from app.services.source_quality_service import SourceQualityService, write_source_report

    with session_for_cli() as session:
        source_run = session.scalar(select(SourceRun).where(SourceRun.run_id == run_id))
        if source_run is None:
            raise typer.BadParameter("source run not found")
        summary = SourceQualityService(session).build_source_run_summary(source_run)
        md_path, json_path = write_source_report(summary, Path("reports"), "source-run")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")


@report_app.command("raw-quality")
def report_raw_quality(source_run: Annotated[str, typer.Option()]) -> None:
    from app.db.models.source_run import SourceRun
    from app.services.source_quality_service import SourceQualityService, write_source_report

    with session_for_cli() as session:
        run = session.scalar(select(SourceRun).where(SourceRun.run_id == source_run))
        if run is None:
            raise typer.BadParameter("source run not found")
        summary = SourceQualityService(session).build_source_run_summary(run)
        md_path, json_path = write_source_report(summary, Path("reports"), "raw-quality")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")


@normalize_app.command("run")
def normalize_run(
    campaign: Annotated[str, typer.Option()],
    source_run: Annotated[str | None, typer.Option()] = None,
    all_raw: Annotated[bool, typer.Option("--all-raw")] = False,
    limit: Annotated[int | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.core.enums import NormalizationOperation
    from app.services.candidate_builder_service import CandidateBuilderService
    from app.services.candidate_report_service import CandidateReportService

    live = _commit_mode(dry_run, commit)
    if not source_run and not all_raw:
        raise typer.BadParameter("Provide --source-run or --all-raw.")
    with session_for_cli() as session:
        service = CandidateBuilderService(session)
        run = service.start_run(
            NormalizationOperation.NORMALIZE_RAW_RECORDS,
            campaign_slug=campaign,
            source_run_id=source_run,
            dry_run=not live,
        )
        raw_records = service.raw_records(None if all_raw else source_run, limit)
        service.build_from_raw(raw_records, run, commit=live)
        md_path, json_path, report = CandidateReportService(session).write_candidate_report(
            Path("reports")
        )
    console.print(f"normalization_run_id={run.run_id}")
    console.print(f"report={md_path}")
    console.print(f"json={json_path}")
    console.print(f"verdict={report['final_verdict']}")


@normalize_app.command("rebuild")
def normalize_rebuild(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.core.enums import NormalizationOperation, NormalizationRunStatus
    from app.services.candidate_builder_service import CandidateBuilderService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        builder = CandidateBuilderService(session)
        run = builder.start_run(
            NormalizationOperation.REBUILD_CANDIDATES,
            campaign_slug=campaign,
            dry_run=not live,
        )
        run.status = (
            NormalizationRunStatus.DRY_RUN_ONLY
            if not live
            else NormalizationRunStatus.COMPLETED
        )
        session.commit()
    console.print(f"normalization_run_id={run.run_id}")
    console.print(f"status={run.status.value}")


@dedupe_app.command("run")
def dedupe_run(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.dedupe_cluster_service import DedupeClusterService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run_id, clusters = DedupeClusterService(session).run(campaign, commit=live)
    console.print(f"normalization_run_id={run_id}")
    console.print(f"duplicate_clusters={len(clusters)}")


@quality_app.command("candidates")
def quality_candidates(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.db.models.candidate_business import CandidateBusiness
    from app.services.candidate_quality_service import CandidateQualityService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        candidates = session.scalars(select(CandidateBusiness)).all()
        if live:
            service = CandidateQualityService(session)
            for candidate in candidates:
                service.apply(candidate)
        ready = sum(
            1 for item in candidates if item.status.value == "READY_FOR_WEBSITE_VERIFICATION"
        )
    console.print(f"candidate_count={len(candidates)}")
    console.print(f"ready_for_phase_4={ready}")


@evidence_app.command("consolidate")
def evidence_consolidate(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.db.models.candidate_business import CandidateBusiness
    from app.services.candidate_evidence_service import CandidateEvidenceService

    live = _commit_mode(dry_run, commit)
    count = 0
    with session_for_cli() as session:
        candidates = session.scalars(select(CandidateBusiness)).all()
        service = CandidateEvidenceService(session)
        for candidate in candidates:
            count += len(service.consolidate_for_candidate(candidate.id, commit=live))
    console.print(f"candidate_count={len(candidates)}")
    console.print(f"evidence_rows={'planned' if not live else 'written'}:{count}")


@report_app.command("candidates")
def report_candidates(campaign: Annotated[str, typer.Option()]) -> None:
    from app.services.candidate_report_service import CandidateReportService

    with session_for_cli() as session:
        md_path, json_path, report = CandidateReportService(session).write_candidate_report(
            Path("reports")
        )
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"verdict={report['final_verdict']}")


@report_app.command("manual-review")
def report_manual_review(campaign: Annotated[str, typer.Option()]) -> None:
    from app.services.candidate_report_service import CandidateReportService

    with session_for_cli() as session:
        md_path, csv_path = CandidateReportService(session).write_manual_review_report(
            Path("reports")
        )
    console.print(f"markdown={md_path}")
    console.print(f"csv={csv_path}")


@verify_app.command("plan")
def verify_plan(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
) -> None:
    from app.services.web_presence_decision_orchestrator import Phase4VerificationOrchestrator

    with session_for_cli() as session:
        candidates, query_count = Phase4VerificationOrchestrator(
            get_settings(), session
        ).plan(limit)
    console.print(f"eligible_candidates={len(candidates)}")
    console.print(f"estimated_queries={query_count}")
    console.print("network_calls=not-called")


def _run_phase4_verify(operation: str, limit: int, dry_run: bool, commit: bool) -> None:
    from app.core.enums import VerificationRunStatus
    from app.services.phase4_report_service import Phase4ReportService
    from app.services.tavily_search_service import TavilySearchService
    from app.services.web_presence_decision_orchestrator import Phase4VerificationOrchestrator

    settings = get_settings()
    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        orchestrator = Phase4VerificationOrchestrator(settings, session)
        candidates, query_count = orchestrator.plan(limit)
        if live and settings.phase4_live_url_probe:
            # Free keyless verification: direct URL probe, no Tavily search API required.
            run = orchestrator.full_review(limit, commit=True)
        elif live:
            allowed, reason = TavilySearchService(settings, session).can_execute(query_count)
            if not allowed:
                run = orchestrator.start_run(
                    VerificationRunOperation.PHASE4_FULL_REVIEW,
                    False,
                    candidates,
                )
                run.status = (
                    VerificationRunStatus.BLOCKED_BY_BUDGET
                    if "BUDGET" in reason
                    else VerificationRunStatus.BLOCKED_BY_CONFIG
                    if "KEY" in reason
                    else VerificationRunStatus.BLOCKED_BY_SAFETY
                )
                run.metadata_json = {"blocked_reason": reason, "query_count": query_count}
                session.commit()
            else:
                run = orchestrator.full_review(limit, commit=True)
        else:
            run = orchestrator.full_review(limit, commit=False)
        md_path, json_path, csv_path, report = Phase4ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"verification_run_id={run.run_id}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"csv={csv_path}")
    console.print(f"verdict={report['final_verdict']}")


@verify_app.command("websites")
def verify_websites(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    _run_phase4_verify("websites", limit, dry_run, commit)


@verify_app.command("contacts")
def verify_contacts(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    _run_phase4_verify("contacts", limit, dry_run, commit)


@verify_app.command("full")
def verify_full(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    _run_phase4_verify("full", limit, dry_run, commit)


@report_app.command("verification")
def report_verification(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.verification_run import VerificationRun
    from app.services.phase4_report_service import Phase4ReportService

    with session_for_cli() as session:
        run = session.scalar(select(VerificationRun).where(VerificationRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("verification run not found")
        md_path, json_path, csv_path, report = Phase4ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"csv={csv_path}")
    console.print(f"verdict={report['final_verdict']}")


@score_app.command("candidates")
def score_candidates(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 50,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.lead_scoring_service import LeadScoringService
    from app.services.phase5_report_service import Phase5ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = LeadScoringService(session).score_candidates(campaign, limit=limit, commit=live)
        md_path, json_path, pilot_path, manual_path, report = Phase5ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"scoring_run_id={run.run_id}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"pilot_csv={pilot_path}")
    console.print(f"manual_review_csv={manual_path}")
    console.print(f"verdict={report['final_verdict']}")
    console.print(
        "external_calls=not-called "
        "email_generation=not-implemented "
        "email_sending=not-implemented"
    )


@score_app.command("explain")
def score_explain(candidate_id: Annotated[int, typer.Option()]) -> None:
    from app.services.score_explanation_service import ScoreExplanationService

    with session_for_cli() as session:
        explanation = ScoreExplanationService(session).explain(candidate_id)
    for key, value in explanation.items():
        console.print(f"{key}={value}")


@campaign_app.command("select")
def campaign_select(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.lead_scoring_service import LeadScoringService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = LeadScoringService(session).score_candidates(campaign, limit=50, commit=live)
    console.print(f"scoring_run_id={run.run_id}")
    console.print("campaign_selection=completed_without_external_calls")


@pilot_app.command("build-batch")
def pilot_build_batch(
    campaign: Annotated[str, typer.Option()],
    batch_name: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.phase5_report_service import Phase5ReportService
    from app.services.pilot_batch_selection_service import PilotBatchSelectionService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run, selected = PilotBatchSelectionService(session).build(
            campaign, batch_name, limit=limit, commit=live
        )
        md_path, json_path, pilot_path, manual_path, report = Phase5ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"scoring_run_id={run.run_id}")
    console.print(f"selected={len(selected)}")
    console.print(f"pilot_csv={pilot_path}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"manual_review_csv={manual_path}")
    console.print(f"verdict={report['final_verdict']}")


@pilot_app.command("audit")
def pilot_audit(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.pilot_audit_service import PilotAuditService

    if dry_run == commit:
        raise typer.BadParameter("Use exactly one of --dry-run or --commit.")
    with session_for_cli() as session:
        run, result = PilotAuditService(session, get_settings()).run(campaign, commit)
        if commit:
            session.commit()
    console.print(f"pilot_audit_run_id={run.run_id}")
    console.print(f"status={run.status}")
    console.print(f"dry_run={run.dry_run}")
    console.print("outbound_actions=false")
    paths = result.get("paths", {})
    if isinstance(paths, dict):
        for key, value in paths.items():
            console.print(f"{key}={value}")


@pilot_app.command("report")
def pilot_report(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.pilot_audit_run import PilotAuditRun
    from app.services.final_pilot_report_service import FinalPilotReportService

    with session_for_cli() as session:
        run = session.scalar(select(PilotAuditRun).where(PilotAuditRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("pilot audit run not found")
        paths = FinalPilotReportService(session).write(run, Path("reports"))
    for key, value in paths.items():
        console.print(f"{key}={value}")


@pilot_app.command("fixpacks")
def pilot_fixpacks(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.fix_pack_recommendation import FixPackRecommendation
    from app.db.models.pilot_audit_run import PilotAuditRun

    with session_for_cli() as session:
        run = session.scalar(select(PilotAuditRun).where(PilotAuditRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("pilot audit run not found")
        rows = session.scalars(
            select(FixPackRecommendation).where(FixPackRecommendation.pilot_audit_run_id == run.id)
        ).all()
    for row in rows:
        console.print(f"{row.code} {row.priority} {row.title}")


@pilot_app.command("scale-decision")
def pilot_scale_decision(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.pilot_audit_run import PilotAuditRun
    from app.db.models.scale_decision_record import ScaleDecisionRecord

    with session_for_cli() as session:
        run = session.scalar(select(PilotAuditRun).where(PilotAuditRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("pilot audit run not found")
        decision = session.scalar(
            select(ScaleDecisionRecord).where(ScaleDecisionRecord.pilot_audit_run_id == run.id)
        )
    console.print(f"decision={decision.decision if decision else 'MISSING'}")
    console.print(f"ready_for_scale={decision.ready_for_scale if decision else False}")


@report_app.command("scoring")
def report_scoring(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.scoring_run import ScoringRun
    from app.services.phase5_report_service import Phase5ReportService

    with session_for_cli() as session:
        run = session.scalar(select(ScoringRun).where(ScoringRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("scoring run not found")
        md_path, json_path, pilot_path, manual_path, report = Phase5ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"pilot_csv={pilot_path}")
    console.print(f"manual_review_csv={manual_path}")
    console.print(f"verdict={report['final_verdict']}")


def _run_phase6_insights(campaign: str, limit: int, dry_run: bool, commit: bool) -> None:
    from app.services.business_insight_orchestrator_service import (
        BusinessInsightOrchestratorService,
    )
    from app.services.phase6_report_service import Phase6ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = BusinessInsightOrchestratorService(session).run(
            campaign, limit=limit, commit=live
        )
        md_path, json_path, blocks_path, manual_path, report = Phase6ReportService(
            session
        ).write(run, Path("reports"))
    console.print(f"insight_run_id={run.run_id}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"offer_blocks_csv={blocks_path}")
    console.print(f"manual_review_csv={manual_path}")
    console.print(f"verdict={report['final_verdict']}")
    console.print("external_calls=not-called ai_calls=not-called email_generation=not-generated")


@insight_app.command("generate")
def insight_generate(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    _run_phase6_insights(campaign, limit, dry_run, commit)


@offer_app.command("match")
def offer_match(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    _run_phase6_insights(campaign, limit, dry_run, commit)


@offer_app.command("explain")
def offer_explain(candidate_id: Annotated[int, typer.Option()]) -> None:
    from app.services.offer_explanation_service import OfferExplanationService

    with session_for_cli() as session:
        explanation = OfferExplanationService(session).explain(candidate_id)
    for key, value in explanation.items():
        console.print(f"{key}={value}")


@report_app.command("insights")
def report_insights(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.insight_run import InsightRun
    from app.services.phase6_report_service import Phase6ReportService

    with session_for_cli() as session:
        run = session.scalar(select(InsightRun).where(InsightRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("insight run not found")
        md_path, json_path, blocks_path, manual_path, report = Phase6ReportService(
            session
        ).write(run, Path("reports"))
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"offer_blocks_csv={blocks_path}")
    console.print(f"manual_review_csv={manual_path}")
    console.print(f"verdict={report['final_verdict']}")


@email_app.command("generate")
def email_generate(
    campaign: Annotated[str, typer.Option()],
    batch_name: Annotated[str | None, typer.Option()] = None,
    limit: Annotated[int, typer.Option()] = 10,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.email_writer_service import EmailWriterService
    from app.services.phase7_report_service import Phase7ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = EmailWriterService(session, get_settings()).generate(
            campaign, batch_name, limit, commit=live
        )
        md_path, json_path, csv_path, report = Phase7ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"email_generation_run_id={run.run_id}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"csv={csv_path}")
    console.print(f"verdict={report['final_verdict']}")
    console.print(f"openai_calls_attempted={report['openai_calls_attempted']}")
    console.print("email_sent=false approved_for_sending=false")


@email_app.command("rewrite")
def email_rewrite(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 50,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    """Rewrite TEXT-rejected drafts (status AWAITING_REWRITE) into fresh JUDGE_PENDING variants
    so the next judge pass can re-score them. Bounded per lineage; recipients never change."""
    from app.services.email_writer_service import EmailWriterService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        produced = EmailWriterService(session, get_settings()).rewrite_awaiting_drafts(
            campaign, limit, commit=live
        )
    console.print(f"rewrites_produced={produced}")


@email_app.command("explain")
def email_explain(draft_id: Annotated[int, typer.Option()]) -> None:
    from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
    from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
    from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
    from app.db.models.email_draft_similarity_result import EmailDraftSimilarityResult
    from app.db.models.email_draft_variant import EmailDraftVariant

    with session_for_cli() as session:
        draft = session.get(EmailDraftVariant, draft_id)
        if draft is None:
            raise typer.BadParameter("draft not found")
        console.print(f"candidate_business_id={draft.candidate_business_id}")
        console.print(f"subject={draft.subject_text}")
        console.print(f"body={draft.body_text}")
        console.print(f"campaign_lane={draft.campaign_lane}")
        evidence = session.scalars(
            select(EmailDraftEvidenceLink).where(
                EmailDraftEvidenceLink.email_draft_variant_id == draft_id
            )
        ).all()
        claims = session.scalars(
            select(EmailDraftClaimUsage).where(
                EmailDraftClaimUsage.email_draft_variant_id == draft_id
            )
        ).all()
        precheck = session.scalar(
            select(EmailDraftPrecheckResult).where(
                EmailDraftPrecheckResult.email_draft_variant_id == draft_id
            )
        )
        similarity = session.scalar(
            select(EmailDraftSimilarityResult).where(
                EmailDraftSimilarityResult.email_draft_variant_id == draft_id
            )
        )
        console.print(f"evidence={evidence}")
        console.print(f"claims={claims}")
        console.print(f"precheck={precheck}")
        console.print(f"similarity={similarity}")
        console.print("next_step=Phase 8 judge")


@report_app.command("email-generation")
def report_email_generation(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.email_generation_run import EmailGenerationRun
    from app.services.phase7_report_service import Phase7ReportService

    with session_for_cli() as session:
        run = session.scalar(select(EmailGenerationRun).where(EmailGenerationRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("email generation run not found")
        md_path, json_path, csv_path, report = Phase7ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"csv={csv_path}")
    console.print(f"verdict={report['final_verdict']}")


@judge_app.command("emails")
def judge_emails(
    campaign: Annotated[str, typer.Option()],
    run_id: Annotated[str | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
    from app.services.phase8_report_service import Phase8ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = EmailJudgeOrchestratorService(session, get_settings()).judge_emails(
            campaign, run_id, commit=live
        )
        md_path, json_path, human_csv, rewrite_csv, blocked_csv, report = Phase8ReportService(
            session
        ).write(run, Path("reports"))
    console.print(f"email_judge_run_id={run.run_id}")
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"human_review_csv={human_csv}")
    console.print(f"rewrite_csv={rewrite_csv}")
    console.print(f"blocked_csv={blocked_csv}")
    console.print(f"verdict={report['final_verdict']}")
    console.print("email_sent=false approved_for_sending=false")


@judge_app.command("variant")
def judge_variant(
    draft_id: Annotated[int, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.db.models.email_draft_variant import EmailDraftVariant
    from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        draft = session.get(EmailDraftVariant, draft_id)
        if draft is None:
            raise typer.BadParameter("draft not found")
        # Campaign is not material for a single draft in this private CLI.
        run = EmailJudgeOrchestratorService(session, get_settings()).judge_emails(
            "auckland-local-website-pilot", None, commit=live, limit=1
        )
    console.print(f"email_judge_run_id={run.run_id}")


@judge_app.command("explain")
def judge_explain(draft_id: Annotated[int, typer.Option()]) -> None:
    from app.db.models.email_judge_decision import EmailJudgeDecision
    from app.db.models.email_judge_finding import EmailJudgeFinding
    from app.db.models.email_rewrite_brief import EmailRewriteBrief

    with session_for_cli() as session:
        decision = session.scalar(
            select(EmailJudgeDecision)
            .where(EmailJudgeDecision.email_draft_variant_id == draft_id)
            .order_by(EmailJudgeDecision.id.desc())
        )
        findings = session.scalars(
            select(EmailJudgeFinding).where(EmailJudgeFinding.email_draft_variant_id == draft_id)
        ).all()
        brief = session.scalar(
            select(EmailRewriteBrief).where(EmailRewriteBrief.email_draft_variant_id == draft_id)
        )
    console.print(f"decision={decision.decision.value if decision else None}")
    console.print(f"findings={[f.message for f in findings]}")
    console.print(f"rewrite_brief={brief.rewrite_reason if brief else None}")
    console.print("next_step=Phase 9 human review queue")


@report_app.command("judge")
def report_judge(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.email_judge_run import EmailJudgeRun
    from app.services.phase8_report_service import Phase8ReportService

    with session_for_cli() as session:
        run = session.scalar(select(EmailJudgeRun).where(EmailJudgeRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("judge run not found")
        md_path, json_path, human_csv, rewrite_csv, blocked_csv, report = Phase8ReportService(
            session
        ).write(run, Path("reports"))
    console.print(f"markdown={md_path}")
    console.print(f"json={json_path}")
    console.print(f"human_review_csv={human_csv}")
    console.print(f"rewrite_csv={rewrite_csv}")
    console.print(f"blocked_csv={blocked_csv}")
    console.print(f"verdict={report['final_verdict']}")


@review_app.command("build-queue")
def review_build_queue(
    campaign: Annotated[str, typer.Option()],
    judge_run_id: Annotated[str | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.human_review_queue_service import HumanReviewQueueService
    from app.services.review_pack_export_service import ReviewPackExportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = HumanReviewQueueService(session, get_settings()).build_queue(
            campaign, judge_run_id, live
        )
        md, csv_path, json_path = ReviewPackExportService(session).export(run, Path("reports"))
    console.print(f"human_review_run_id={run.run_id}")
    console.print(f"markdown={md}")
    console.print(f"csv={csv_path}")
    console.print(f"json={json_path}")
    console.print("email_sent=false scheduled=false smtp=false")


@review_app.command("export")
def review_export(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.human_review_run import HumanReviewRun
    from app.services.review_pack_export_service import ReviewPackExportService

    with session_for_cli() as session:
        run = session.scalar(select(HumanReviewRun).where(HumanReviewRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("human review run not found")
        md, csv_path, json_path = ReviewPackExportService(session).export(run, Path("reports"))
    console.print(f"markdown={md}")
    console.print(f"csv={csv_path}")
    console.print(f"json={json_path}")


@review_app.command("approve")
def review_approve(
    queue_item_id: Annotated[int, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    notes: Annotated[str | None, typer.Option()] = None,
) -> None:
    from app.services.human_decision_service import HumanDecisionService

    with session_for_cli() as session:
        decision = HumanDecisionService(session, get_settings()).approve(
            queue_item_id, reviewer, notes
        )
        session.commit()
    console.print(f"decision={decision.decision.value}")
    console.print("ready_for_phase10_only=true email_sent=false")


@review_app.command("reject")
def review_reject(
    queue_item_id: Annotated[int, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.services.human_decision_service import HumanDecisionService

    with session_for_cli() as session:
        decision = HumanDecisionService(session, get_settings()).reject(
            queue_item_id, reviewer, reason
        )
        session.commit()
    console.print(f"decision={decision.decision.value}")


@review_app.command("hold")
def review_hold(
    queue_item_id: Annotated[int, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.services.human_decision_service import HumanDecisionService

    with session_for_cli() as session:
        decision = HumanDecisionService(session, get_settings()).hold(
            queue_item_id, reviewer, reason
        )
        session.commit()
    console.print(f"decision={decision.decision.value}")


@review_app.command("return-rewrite")
def review_return_rewrite(
    queue_item_id: Annotated[int, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.services.human_decision_service import HumanDecisionService

    with session_for_cli() as session:
        decision = HumanDecisionService(session, get_settings()).return_rewrite(
            queue_item_id, reviewer, reason
        )
        session.commit()
    console.print(f"decision={decision.decision.value}")


@review_app.command("return-judge")
def review_return_judge(
    queue_item_id: Annotated[int, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.services.human_decision_service import HumanDecisionService

    with session_for_cli() as session:
        decision = HumanDecisionService(session, get_settings()).return_judge(
            queue_item_id, reviewer, reason
        )
        session.commit()
    console.print(f"decision={decision.decision.value}")


@review_app.command("export-edit-template")
def review_export_edit_template(queue_item_id: Annotated[int, typer.Option()]) -> None:
    from app.db.models.email_draft_variant import EmailDraftVariant
    from app.db.models.human_review_queue_item import HumanReviewQueueItem

    with session_for_cli() as session:
        item = session.get(HumanReviewQueueItem, queue_item_id)
        if item is None:
            raise typer.BadParameter("queue item not found")
        draft = session.get(EmailDraftVariant, item.email_draft_variant_id)
        if draft is None:
            raise typer.BadParameter("draft not found")
        path = Path("reports") / f"phase9-edit-template-{queue_item_id}.txt"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"Subject: {draft.subject_text}\n\n{draft.body_text}\n", encoding="utf-8")
    console.print(f"path={path}")


@review_app.command("import-edit")
def review_import_edit(
    queue_item_id: Annotated[int, typer.Option()],
    file: Annotated[Path, typer.Option()],
    editor: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.services.manual_edit_service import ManualEditService

    content = file.read_text(encoding="utf-8")
    subject = "Manual edited subject"
    body = content
    if content.startswith("Subject:"):
        first, _, rest = content.partition("\n")
        subject = first.replace("Subject:", "").strip()
        body = rest.strip()
    with session_for_cli() as session:
        version = ManualEditService(session, get_settings()).create_version(
            queue_item_id, subject, body, editor, reason
        )
        session.commit()
    console.print(f"version={version.version_number}")
    console.print(f"requires_rejudge={version.requires_rejudge}")


@review_app.command("final-check")
def review_final_check(queue_item_id: Annotated[int, typer.Option()]) -> None:
    from app.services.final_pre_send_review_service import FinalPreSendReviewService

    with session_for_cli() as session:
        check = FinalPreSendReviewService(session, get_settings()).run(queue_item_id)
        session.commit()
    console.print(f"check_status={check.check_status.value}")
    console.print(f"risk_flags={check.risk_flags_json}")


@report_app.command("human-review")
def report_human_review(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.human_review_run import HumanReviewRun
    from app.services.phase9_report_service import Phase9ReportService

    with session_for_cli() as session:
        run = session.scalar(select(HumanReviewRun).where(HumanReviewRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("human review run not found")
        md, approved, blocked, returned, report = Phase9ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"markdown={md}")
    console.print(f"approved_csv={approved}")
    console.print(f"blocked_csv={blocked}")
    console.print(f"returned_csv={returned}")
    console.print(f"verdict={report['final_verdict']}")


@send_app.command("build-queue")
def send_build_queue(
    campaign: Annotated[str, typer.Option()],
    human_review_run_id: Annotated[str | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.phase10_report_service import Phase10ReportService
    from app.services.send_queue_service import SendQueueService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = SendQueueService(session, get_settings()).build_queue(
            campaign, human_review_run_id, live
        )
        md, json_path, sent, blocked, errors, plan, report = Phase10ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"send_queue_run_id={run.run_id}")
    console.print(f"markdown={md}")
    console.print(f"json={json_path}")
    console.print(f"send_plan_csv={plan}")
    console.print(f"verdict={report['final_verdict']}")


@send_app.command("provider-check")
def send_provider_check(provider: Annotated[str, typer.Option()]) -> None:
    from app.services.provider_readiness_service import ProviderReadinessService

    with session_for_cli() as session:
        ok, gaps, row = ProviderReadinessService(session, get_settings()).check()
        session.commit()
    console.print(f"provider={provider}")
    console.print(f"provider_slug={row.provider_slug}")
    console.print(f"ready={ok}")
    console.print(f"gaps={gaps}")
    console.print("secrets=redacted")
    console.print("test_email_sent=false")


@send_app.command("run")
def send_run(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 5,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.controlled_send_service import ControlledSendService
    from app.services.phase10_report_service import Phase10ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = ControlledSendService(session, get_settings()).run(campaign, limit, live)
        md, json_path, sent, blocked, errors, plan, report = Phase10ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"send_queue_run_id={run.run_id}")
    console.print(f"markdown={md}")
    console.print(f"json={json_path}")
    console.print(f"sent_csv={sent}")
    console.print(f"blocked_csv={blocked}")
    console.print(f"verdict={report['final_verdict']}")


@send_app.command("suppress")
def send_suppress(
    email: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import SuppressionReason
    from app.db.models.suppression import SuppressionList

    with session_for_cli() as session:
        session.add(
            SuppressionList(email=email.lower(), reason=SuppressionReason(reason), source="cli")
        )
        session.commit()
    console.print("suppression_added=true")


@send_app.command("suppress-domain")
def send_suppress_domain(
    domain: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import SuppressionReason
    from app.db.models.suppression import SuppressionList

    with session_for_cli() as session:
        session.add(
            SuppressionList(domain=domain.lower(), reason=SuppressionReason(reason), source="cli")
        )
        session.commit()
    console.print("suppression_added=true")


@send_app.command("suppression-import")
def send_suppression_import(
    file: Annotated[Path, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.suppression_import_service import SuppressionImportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = SuppressionImportService(session).run(file, live)
    console.print(f"suppression_import_run_id={run.run_id}")
    console.print(f"valid_rows={run.valid_rows}")
    console.print(f"imported_rows={run.imported_rows}")


@send_app.command("hold-item")
def send_hold_item(
    queue_item_id: Annotated[int, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import EmailSendQueueStatus, SendAuditAction
    from app.db.models.email_send_queue import EmailSendQueue
    from app.db.models.send_audit_event import SendAuditEvent

    if not reason:
        raise typer.BadParameter("reason required")
    with session_for_cli() as session:
        item = session.get(EmailSendQueue, queue_item_id)
        if item is None:
            raise typer.BadParameter("queue item not found")
        item.queue_status = EmailSendQueueStatus.HELD_BY_OPERATOR
        item.hold_reason = reason
        session.add(
            SendAuditEvent(
                email_send_queue_id=item.id,
                actor="cli",
                action=SendAuditAction.QUEUE_HELD,
                reason=reason,
            )
        )
        session.commit()
    console.print("held=true")


@send_app.command("cancel-item")
def send_cancel_item(
    queue_item_id: Annotated[int, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import EmailSendQueueStatus, SendAuditAction
    from app.db.models.email_send_queue import EmailSendQueue
    from app.db.models.send_audit_event import SendAuditEvent

    if not reason:
        raise typer.BadParameter("reason required")
    with session_for_cli() as session:
        item = session.get(EmailSendQueue, queue_item_id)
        if item is None:
            raise typer.BadParameter("queue item not found")
        item.queue_status = EmailSendQueueStatus.CANCELLED_BY_OPERATOR
        item.cancel_reason = reason
        session.add(
            SendAuditEvent(
                email_send_queue_id=item.id,
                actor="cli",
                action=SendAuditAction.QUEUE_CANCELLED,
                reason=reason,
            )
        )
        session.commit()
    console.print("cancelled=true")


@report_app.command("sending")
def report_sending(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.send_queue_run import SendQueueRun
    from app.services.phase10_report_service import Phase10ReportService

    with session_for_cli() as session:
        run = session.scalar(select(SendQueueRun).where(SendQueueRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("send queue run not found")
        md, json_path, sent, blocked, errors, plan, report = Phase10ReportService(session).write(
            run, Path("reports")
        )
    console.print(f"markdown={md}")
    console.print(f"json={json_path}")
    console.print(f"sent_csv={sent}")
    console.print(f"blocked_csv={blocked}")
    console.print(f"errors_csv={errors}")
    console.print(f"plan_csv={plan}")
    console.print(f"verdict={report['final_verdict']}")


@inbox_app.command("plan")
def inbox_plan(mailbox: Annotated[str, typer.Option()] = "default") -> None:
    from app.services.mailbox_sync_service import MailboxSyncService

    with session_for_cli() as session:
        plan = MailboxSyncService(session, get_settings()).plan(mailbox)
        session.commit()
    for key, value in plan.items():
        console.print(f"{key}={value}")


@inbox_app.command("sync")
def inbox_sync(
    mailbox: Annotated[str, typer.Option()] = "default",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.mailbox_sync_service import MailboxSyncService
    from app.services.phase11_report_service import Phase11ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        run = MailboxSyncService(session, get_settings()).sync(mailbox, live)
        paths = Phase11ReportService(session).write(run, Path("reports"))
        session.commit()
    console.print(f"inbox_sync_run_id={run.run_id}")
    console.print(f"markdown={paths[0]}")
    console.print(f"json={paths[-1]}")
    console.print("outbound_sent=false")


@inbox_app.command("classify")
def inbox_classify(run_id: Annotated[str, typer.Option()], commit: bool = False) -> None:
    from app.db.models.email_send_queue import EmailSendQueue
    from app.db.models.inbound_email_message import InboundEmailMessage
    from app.db.models.inbox_sync_run import InboxSyncRun
    from app.services.clean_reply_extraction_service import CleanReplyExtractionService
    from app.services.human_task_service import HumanTaskService
    from app.services.lead_response_status_service import LeadResponseStatusService
    from app.services.reply_classification_service import ReplyClassificationService
    from app.services.suppression_from_inbound_service import SuppressionFromInboundService
    from app.services.thread_matching_service import ThreadMatchingService

    if not commit:
        raise typer.BadParameter("--commit required for classification writes")
    with session_for_cli() as session:
        run = session.scalar(select(InboxSyncRun).where(InboxSyncRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("sync run not found")
        messages = session.scalars(
            select(InboundEmailMessage).where(InboundEmailMessage.sync_run_id == run.id)
        ).all()
        classified = 0
        for message in messages:
            CleanReplyExtractionService(session).extract(message)
            ThreadMatchingService(session).match(message)
            classification = ReplyClassificationService(session, get_settings()).classify(message)
            SuppressionFromInboundService(session, get_settings()).apply_for_reply(
                message, classification
            )
            if message.matched_send_queue_id:
                queue = session.get(EmailSendQueue, message.matched_send_queue_id)
                if queue:
                    LeadResponseStatusService(session).update(
                        message, classification, queue.campaign_id
                    )
            HumanTaskService(session, get_settings()).create_for_classification(
                message, classification
            )
            classified += 1
        session.commit()
    console.print(f"classified={classified}")
    console.print("outbound_sent=false")


@inbox_app.command("process-bounces")
def inbox_process_bounces(run_id: Annotated[str, typer.Option()], commit: bool = False) -> None:
    from app.db.models.inbound_email_message import InboundEmailMessage
    from app.db.models.inbox_sync_run import InboxSyncRun
    from app.services.bounce_detection_service import BounceDetectionService
    from app.services.suppression_from_inbound_service import SuppressionFromInboundService

    if not commit:
        raise typer.BadParameter("--commit required for bounce writes")
    with session_for_cli() as session:
        run = session.scalar(select(InboxSyncRun).where(InboxSyncRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("sync run not found")
        count = 0
        for message in session.scalars(
            select(InboundEmailMessage).where(InboundEmailMessage.sync_run_id == run.id)
        ):
            bounce = BounceDetectionService(session).create_event(message)
            if bounce:
                SuppressionFromInboundService(session, get_settings()).apply_for_bounce(bounce)
                count += 1
        session.commit()
    console.print(f"bounces_processed={count}")
    console.print("outbound_sent=false")


@inbox_app.command("apply-suppression")
def inbox_apply_suppression(run_id: Annotated[str, typer.Option()], commit: bool = False) -> None:
    from app.db.models.inbound_email_message import InboundEmailMessage
    from app.db.models.inbox_sync_run import InboxSyncRun
    from app.db.models.reply_classification import ReplyClassification
    from app.services.suppression_from_inbound_service import SuppressionFromInboundService

    if not commit:
        raise typer.BadParameter("--commit required for suppression writes")
    with session_for_cli() as session:
        run = session.scalar(select(InboxSyncRun).where(InboxSyncRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("sync run not found")
        applied = 0
        messages = session.scalars(
            select(InboundEmailMessage).where(InboundEmailMessage.sync_run_id == run.id)
        ).all()
        for message in messages:
            classification = session.scalar(
                select(ReplyClassification).where(
                    ReplyClassification.inbound_message_id == message.id
                )
            )
            if classification and SuppressionFromInboundService(
                session, get_settings()
            ).apply_for_reply(message, classification):
                applied += 1
        session.commit()
    console.print(f"suppressions_applied={applied}")


@inbox_app.command("override")
def inbox_override(
    message_id: Annotated[int, typer.Option()],
    classification: Annotated[str, typer.Option()],
    reviewer: Annotated[str, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import ReplyClassificationValue, ReplyClassifierType
    from app.db.models.inbound_email_message import InboundEmailMessage
    from app.db.models.reply_classification import ReplyClassification
    from app.db.models.reply_manual_override import ReplyManualOverride

    with session_for_cli() as session:
        message = session.get(InboundEmailMessage, message_id)
        if message is None:
            raise typer.BadParameter("message not found")
        old = session.scalar(
            select(ReplyClassification).where(ReplyClassification.inbound_message_id == message.id)
        )
        old_value = old.classification if old else ReplyClassificationValue.UNKNOWN_NEEDS_REVIEW
        new_value = ReplyClassificationValue(classification)
        session.add(
            ReplyManualOverride(
                inbound_message_id=message.id,
                candidate_business_id=message.matched_candidate_business_id,
                old_classification=old_value,
                new_classification=new_value,
                reviewer=reviewer,
                reason=reason,
            )
        )
        session.add(
            ReplyClassification(
                inbound_message_id=message.id,
                candidate_business_id=message.matched_candidate_business_id,
                classification=new_value,
                confidence=1.0,
                classifier_type=ReplyClassifierType.MANUAL,
                manual_override=True,
                signals_json={"reviewer": reviewer, "reason": reason},
            )
        )
        session.commit()
    console.print("override_saved=true")
    console.print("outbound_sent=false")


@report_app.command("inbox")
def report_inbox(run_id: Annotated[str, typer.Option()]) -> None:
    from app.db.models.inbox_sync_run import InboxSyncRun
    from app.services.phase11_report_service import Phase11ReportService

    with session_for_cli() as session:
        run = session.scalar(select(InboxSyncRun).where(InboxSyncRun.run_id == run_id))
        if run is None:
            raise typer.BadParameter("sync run not found")
        paths = Phase11ReportService(session).write(run, Path("reports"))
    console.print(f"markdown={paths[0]}")
    console.print(f"replies_csv={paths[1]}")
    console.print(f"bounces_csv={paths[2]}")
    console.print(f"tasks_csv={paths[3]}")
    console.print(f"unmatched_csv={paths[4]}")
    console.print(f"json={paths[5]}")


@opportunity_app.command("build")
def opportunity_build(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.services.opportunity_service import OpportunityService
    from app.services.phase12_report_service import Phase12ReportService

    live = _commit_mode(dry_run, commit)
    with session_for_cli() as session:
        summary = OpportunityService(session, get_settings()).build_for_campaign(campaign, live)
        paths = Phase12ReportService(session).write(Path("reports"))
        if live:
            session.commit()
    console.print(f"opportunities_created={summary['opportunities_created']}")
    console.print(f"human_tasks_created={summary['tasks']}")
    console.print(f"markdown={paths[0]}")
    console.print(f"json={paths[1]}")
    console.print("outbound_sent=false")


@opportunity_app.command("plan-response")
def opportunity_plan_response(
    opportunity_id: Annotated[int, typer.Option()],
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    from app.db.models.opportunity_record import OpportunityRecord
    from app.services.response_guidance_service import ResponseGuidanceService

    if not commit:
        raise typer.BadParameter("--commit required for response guidance writes")
    with session_for_cli() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
        if opp is None:
            raise typer.BadParameter("opportunity not found")
        ResponseGuidanceService(session).create(opp)
        session.commit()
    console.print("manual_response_plan_ready=true")
    console.print("outbound_sent=false")


@opportunity_app.command("explain")
def opportunity_explain(opportunity_id: Annotated[int, typer.Option()]) -> None:
    from app.db.models.opportunity_record import OpportunityRecord

    with session_for_cli() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
        if opp is None:
            raise typer.BadParameter("opportunity not found")
        console.print(f"status={opp.opportunity_status.value}")
        console.print(f"type={opp.opportunity_type.value}")
        console.print("next_action=manual human response planning only")


@opportunity_app.command("close")
def opportunity_close(
    opportunity_id: Annotated[int, typer.Option()],
    reason: Annotated[str, typer.Option()],
) -> None:
    from app.core.enums import OpportunityStatus
    from app.db.models.opportunity_record import OpportunityRecord

    if not reason:
        raise typer.BadParameter("reason required")
    with session_for_cli() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
        if opp is None:
            raise typer.BadParameter("opportunity not found")
        opp.opportunity_status = OpportunityStatus.CLOSED_NOT_INTERESTED
        session.commit()
    console.print("closed=true")


@report_app.command("opportunities")
def report_opportunities(campaign: Annotated[str, typer.Option()] = "") -> None:
    from app.services.phase12_report_service import Phase12ReportService

    with session_for_cli() as session:
        paths = Phase12ReportService(session).write(Path("reports"))
    console.print(f"markdown={paths[0]}")
    console.print(f"json={paths[1]}")
    console.print(f"tasks_csv={paths[2]}")
    console.print(f"pricing_csv={paths[3]}")
    console.print("outbound_sent=false")


@report_app.command("sales-workspace")
def report_sales_workspace_command(campaign: Annotated[str, typer.Option()] = "") -> None:
    report_sales_workspace(campaign)


@ops_app.command("readiness")
def ops_readiness(campaign: Annotated[str, typer.Option()]) -> None:
    from app.db.models.campaign import Campaign
    from app.services.ops_readiness_service import OpsReadinessService

    with session_for_cli() as session:
        row = session.scalar(select(Campaign).where(Campaign.slug == campaign))
        checks = OpsReadinessService(session, get_settings()).run(row.id if row else None, None)
        session.commit()
    for check in checks:
        console.print(f"{check.check_name}: {check.status} severity={check.severity}")
    console.print("outbound_actions=false")


@ops_app.command("export")
def ops_export(campaign: Annotated[str, typer.Option()]) -> None:
    from app.services.backup_export_service import BackupExportService
    from app.services.retention_policy_service import RetentionPolicyService

    with session_for_cli() as session:
        record = BackupExportService(session).record_manifest(None)
        RetentionPolicyService(session, get_settings()).create(None)
        session.commit()
    console.print(f"export_manifest={record.file_path}")
    console.print("env_files_exported=false")
    console.print("secrets_exported=false")


@improvement_app.command("generate")
def improvement_generate(
    campaign: Annotated[str, typer.Option()],
    limit: Annotated[int, typer.Option()] = 25,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    """Separate 'improve your existing website' batch for businesses that already have a site."""
    from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
    from app.services.email_writer_service import EmailWriterService
    from app.services.human_review_queue_service import HumanReviewQueueService

    live = _commit_mode(dry_run, commit)
    settings = get_settings()
    with session_for_cli() as session:
        gen = EmailWriterService(session, settings).generate_improvement(campaign, limit, live)
        judged = EmailJudgeOrchestratorService(session, settings).judge_emails(
            campaign, gen.run_id, commit=live
        )
        review = HumanReviewQueueService(session, settings).build_queue(
            campaign, judged.run_id, live
        )
    console.print("campaign_type=improvement (separate from the no-website batch)")
    console.print(f"improvement_generation_run={gen.run_id} drafts={gen.draft_created_count}")
    console.print(f"judge_run={judged.run_id} verdict={judged.status.value}")
    console.print(f"review_run={review.run_id} queued={review.queued_count}")
    console.print("email_sent=false")


@geo_app.command("countries")
def geo_countries() -> None:
    from app.services.geography_service import GeographyService

    service = GeographyService()
    for country in service.countries():
        big = len(service.cities(country, "big"))
        small = len(service.cities(country, "small"))
        console.print(f"{country}: big={big} small={small} tz={service.timezone(country)}")
    console.print(f"total_cities={service.total_cities()}")


@geo_app.command("cities")
def geo_cities(
    country: Annotated[str, typer.Option()],
    size: Annotated[str, typer.Option()] = "all",
) -> None:
    from app.services.geography_service import GeographyService

    service = GeographyService()
    if service.country(country) is None:
        raise typer.BadParameter(
            f"Unknown country '{country}'. Try one of: {', '.join(service.countries())}"
        )
    cities = service.cities(country, size)
    for city in cities:
        console.print(city)
    console.print(f"count={len(cities)} country={country} size={size}")


@send_app.command("dns-check")
def send_dns_check(domain: Annotated[str, typer.Option()]) -> None:
    """Check SPF/DKIM/DMARC for a sending domain using free DNS-over-HTTPS (no key)."""
    from app.services.email_deliverability_service import EmailDeliverabilityService

    result = EmailDeliverabilityService().check_domain(domain)
    for key, value in result.items():
        console.print(f"{key}: {value}")


@send_app.command("self-test")
def send_self_test(
    to: Annotated[str, typer.Option()],
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    """Send ONE test email to your own address to verify SMTP works. No leads touched."""
    from email.message import EmailMessage

    from app.services.provider_readiness_service import ProviderReadinessService

    settings = get_settings()
    with session_for_cli() as session:
        ok, gaps, provider_config = ProviderReadinessService(session, settings).check()
        session.commit()
    console.print(f"provider_ready={ok} gaps={gaps}")
    from_email = settings.default_from_email or settings.smtp_from_email
    if not commit:
        console.print(f"dry_run=true would_send_from={from_email} to={to}")
        console.print("Add --commit to actually send the self-test (only to your own address).")
        return
    if not ok:
        console.print("blocked: provider config incomplete; fill SMTP_* and DEFAULT_FROM_EMAIL.")
        raise typer.Exit(1)
    from app.services.cpanel_smtp_provider import CpanelSmtpProvider

    message = EmailMessage()
    message["From"] = f"{provider_config.from_name} <{from_email}>"
    message["To"] = to
    message["Subject"] = "A2 Local Lead Engine - SMTP self test"
    message.set_content(
        "This is a self-test from the A2 Local Lead Engine. "
        "If you received it, your SMTP sending is configured correctly. "
        "No lead or campaign data is involved."
    )
    result = CpanelSmtpProvider(settings).send(message, dry_run=False)
    console.print(f"provider_status={result.provider_status.value}")
    console.print(f"error={result.error_type or 'none'} {result.error_message or ''}")


app.add_typer(db_app, name="db")
app.add_typer(config_app, name="config")
app.add_typer(campaign_app, name="campaign")
app.add_typer(safety_app, name="safety")
app.add_typer(report_app, name="report")
app.add_typer(fixtures_app, name="fixtures")
app.add_typer(sources_app, name="sources")
app.add_typer(collect_app, name="collect")
app.add_typer(enrich_app, name="enrich")
app.add_typer(normalize_app, name="normalize")
app.add_typer(dedupe_app, name="dedupe")
app.add_typer(quality_app, name="quality")
app.add_typer(evidence_app, name="evidence")
app.add_typer(verify_app, name="verify")
app.add_typer(score_app, name="score")
app.add_typer(pilot_app, name="pilot")
app.add_typer(ops_app, name="ops")
app.add_typer(insight_app, name="insight")
app.add_typer(offer_app, name="offer")
app.add_typer(email_app, name="email")
app.add_typer(judge_app, name="judge")
app.add_typer(review_app, name="review")
app.add_typer(send_app, name="send")
app.add_typer(inbox_app, name="inbox")
app.add_typer(opportunity_app, name="opportunity")
app.add_typer(sales_workspace_app, name="sales-workspace")
app.add_typer(geo_app, name="geo")
app.add_typer(improvement_app, name="improvement")


if __name__ == "__main__":
    app()
