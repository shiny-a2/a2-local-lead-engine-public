from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PricePositioning, PriceVisibility
from app.db.base import Base, utc_now


class PricePositioningRecommendation(Base):
    __tablename__ = "price_positioning_recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    price_positioning: Mapped[PricePositioning] = mapped_column(Enum(PricePositioning, native_enum=False))
    price_visibility: Mapped[PriceVisibility] = mapped_column(Enum(PriceVisibility, native_enum=False))
    price_risk: Mapped[str] = mapped_column(nullable=False)
    recommended_language_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    blocked_language_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
