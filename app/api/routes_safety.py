from fastapi import APIRouter

from app.core.safety import check_all_operations
from app.settings import get_settings

router = APIRouter()


@router.get("/safety")
def safety() -> list[dict[str, object]]:
    return [check.model_dump() for check in check_all_operations(get_settings())]
