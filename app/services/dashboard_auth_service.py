from fastapi import HTTPException, Request, status

from app.settings import Settings


class DashboardAuthService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def require(self, request: Request) -> None:
        if not self.settings.phase9_review_dashboard_enabled and not self.settings.testing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review dashboard disabled")
        if not self.settings.phase9_basic_auth_enabled:
            return
        # MVP private dashboard guard. Full password verification can be added once deployed.
        if self.settings.phase9_review_username and request.headers.get("x-review-user") != self.settings.phase9_review_username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="review auth required")
