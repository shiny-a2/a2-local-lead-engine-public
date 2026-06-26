from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ComplexityLevel, MaintenanceRisk, OfferModuleType, WordpressFit
from app.db.base import Base, utc_now


class OfferModule(Base):
    __tablename__ = "offer_modules"
    id: Mapped[int] = mapped_column(primary_key=True)
    playbook_id: Mapped[int] = mapped_column(ForeignKey("offer_playbooks.id"))
    module_slug: Mapped[str] = mapped_column(String(160), nullable=False)
    module_name: Mapped[str] = mapped_column(String(255), nullable=False)
    module_type: Mapped[OfferModuleType] = mapped_column(Enum(OfferModuleType, native_enum=False))
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    complexity_level: Mapped[ComplexityLevel] = mapped_column(Enum(ComplexityLevel, native_enum=False))
    implementation_complexity: Mapped[ComplexityLevel] = mapped_column(Enum(ComplexityLevel, native_enum=False))
    maintenance_risk: Mapped[MaintenanceRisk] = mapped_column(Enum(MaintenanceRisk, native_enum=False))
    wordpress_fit: Mapped[WordpressFit] = mapped_column(Enum(WordpressFit, native_enum=False))
    custom_code_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    third_party_dependency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estimated_build_effort: Mapped[str] = mapped_column(String(120), nullable=False)
    economic_angle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_core: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
