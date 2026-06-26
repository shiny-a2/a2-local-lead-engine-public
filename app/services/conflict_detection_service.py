from app.core.enums import ConflictType


class ConflictDetectionService:
    def category_conflict(self, categories: list[str | None]) -> bool:
        present = {category for category in categories if category}
        return len(present) > 1

    def location_conflict(self, suburbs: list[str | None]) -> bool:
        present = {suburb for suburb in suburbs if suburb}
        return len(present) > 1

    def conflict_type_for_shared_field(self, field: str) -> ConflictType:
        if field == "phone":
            return ConflictType.PHONE_SHARED_ACROSS_CANDIDATES
        if field == "website":
            return ConflictType.WEBSITE_SHARED_ACROSS_CANDIDATES
        return ConflictType.NAME_CONFLICT
