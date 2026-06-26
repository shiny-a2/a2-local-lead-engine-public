from dataclasses import asdict, dataclass

from app.core.enums import SensitiveOperation
from app.core.feature_flags import FLAG_REQUIREMENTS, get_flag_value
from app.settings import Settings


@dataclass(frozen=True)
class SafetyCheck:
    allowed: bool
    operation: str
    reason: str
    flag: str
    required_value: bool
    current_value: bool

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def check_operation(settings: Settings, operation: SensitiveOperation) -> SafetyCheck:
    requirement = FLAG_REQUIREMENTS[operation]
    current = get_flag_value(settings, requirement.flag_name)
    return SafetyCheck(
        allowed=current is True,
        operation=operation.value,
        reason="ALLOWED" if current else requirement.reason,
        flag=requirement.flag_name,
        required_value=True,
        current_value=current,
    )


def check_all_operations(settings: Settings) -> list[SafetyCheck]:
    return [check_operation(settings, operation) for operation in SensitiveOperation]

