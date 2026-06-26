from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OfferPackage
from app.db.base import Base, utc_now


class CandidateOfferMatch(Base):
    __tablename__ = "candidate_offer_matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    playbook_id: Mapped[int] = mapped_column(ForeignKey("offer_playbooks.id"))
    offer_package: Mapped[OfferPackage] = mapped_column(Enum(OfferPackage, native_enum=False))
    offer_fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    offer_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    offer_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    internal_offer_analysis: Mapped[str] = mapped_column(String(1500), nullable=False)
    email_safe_offer_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    primary_value_angle: Mapped[str] = mapped_column(String(500), nullable=False)
    secondary_value_angles_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    selected_module_ids_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    excluded_module_ids_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
