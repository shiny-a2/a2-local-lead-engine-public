from fastapi import FastAPI

from app.api.routes_campaigns import router as campaigns_router
from app.api.routes_candidates import router as candidates_router
from app.api.routes_health import router as health_router
from app.api.routes_phase4 import router as phase4_router
from app.api.routes_phase5 import router as phase5_router
from app.api.routes_phase6 import router as phase6_router
from app.api.routes_phase7 import router as phase7_router
from app.api.routes_phase8 import router as phase8_router
from app.api.routes_safety import router as safety_router
from app.api.routes_sources import router as sources_router
from app.api.routes_status import router as status_router
from app.logging_config import configure_logging
from app.settings import get_settings
from app.web.inbox_routes import router as inbox_dashboard_router
from app.web.opportunity_routes import router as opportunity_dashboard_router
from app.web.pilot_governance_routes import router as pilot_governance_dashboard_router
from app.web.review_routes import router as review_dashboard_router
from app.web.sales_workspace_routes import router as sales_workspace_dashboard_router
from app.web.send_routes import router as send_dashboard_router
from app.web.unsubscribe_routes import router as unsubscribe_router
from app.web.webhook_routes import router as webhook_router

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    description="Private/local Phase 1 foundation API. Do not expose publicly.",
)
app.include_router(health_router)
app.include_router(status_router)
app.include_router(campaigns_router)
app.include_router(safety_router)
app.include_router(sources_router)
app.include_router(candidates_router)
app.include_router(phase4_router)
app.include_router(phase5_router)
app.include_router(phase6_router)
app.include_router(phase7_router)
app.include_router(phase8_router)
app.include_router(review_dashboard_router)
app.include_router(send_dashboard_router)
app.include_router(unsubscribe_router)
app.include_router(inbox_dashboard_router)
app.include_router(opportunity_dashboard_router)
app.include_router(sales_workspace_dashboard_router)
app.include_router(pilot_governance_dashboard_router)
app.include_router(webhook_router)
