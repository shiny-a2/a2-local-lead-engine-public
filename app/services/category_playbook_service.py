from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    ComplexityLevel,
    MaintenanceRisk,
    OfferModuleType,
    OfferPackage,
    OfferPlaybookStatus,
    WordpressFit,
)
from app.db.models.offer_module import OfferModule
from app.db.models.offer_playbook import OfferPlaybook


class CategoryPlaybookService:
    def __init__(self, session: Session):
        self.session = session

    def seed_defaults(self) -> None:
        for item in self._playbooks():
            playbook = self.session.scalar(
                select(OfferPlaybook).where(OfferPlaybook.playbook_slug == item["slug"])
            )
            if playbook is None:
                playbook = OfferPlaybook(
                    category=item["category"],
                    playbook_slug=item["slug"],
                    playbook_name=item["name"],
                    status=item["status"],
                    version="v1.0",
                    description=item["description"],
                    default_offer_package=item["package"].value,
                )
                self.session.add(playbook)
                self.session.flush()
            if not self.session.scalar(
                select(OfferModule).where(OfferModule.playbook_id == playbook.id)
            ):
                for module in item["modules"]:
                    self.session.add(OfferModule(playbook_id=playbook.id, **module))
        self.session.commit()

    def active_for_category(self, category: str) -> OfferPlaybook | None:
        return self.session.scalar(
            select(OfferPlaybook).where(
                OfferPlaybook.category == category,
                OfferPlaybook.status == OfferPlaybookStatus.ACTIVE,
            )
        )

    def modules_for(self, playbook_id: int) -> list[OfferModule]:
        return list(self.session.scalars(
            select(OfferModule).where(OfferModule.playbook_id == playbook_id)
        ).all())

    def _module(
        self,
        slug: str,
        name: str,
        module_type: OfferModuleType,
        *,
        core: bool = True,
        complexity: ComplexityLevel = ComplexityLevel.LOW,
        optional: bool = False,
    ) -> dict:
        return {
            "module_slug": slug,
            "module_name": name,
            "module_type": module_type,
            "description": f"{name} module for a conservative first website offer.",
            "complexity_level": complexity,
            "implementation_complexity": complexity,
            "maintenance_risk": MaintenanceRisk.LOW if complexity != ComplexityLevel.HIGH else MaintenanceRisk.MEDIUM,
            "wordpress_fit": WordpressFit.EXCELLENT if not optional else WordpressFit.GOOD,
            "custom_code_required": False,
            "third_party_dependency": None,
            "estimated_build_effort": "small" if complexity == ComplexityLevel.LOW else "moderate",
            "economic_angle": "lower friction customer action",
            "is_core": core,
            "is_optional": optional,
        }

    def _playbooks(self) -> list[dict]:
        return [
            {
                "category": "beauty_salon",
                "slug": "beauty-salon-v1",
                "name": "Beauty Salon Booking Site",
                "status": OfferPlaybookStatus.ACTIVE,
                "package": OfferPackage.BOOKING_SYSTEM_SITE,
                "description": "Booking/enquiry path, service menu, gallery, reviews, and contact.",
                "modules": [
                    self._module("service-menu", "Service Menu", OfferModuleType.MENU),
                    self._module("booking-request", "Booking Request", OfferModuleType.BOOKING),
                    self._module("gallery", "Gallery", OfferModuleType.GALLERY),
                    self._module("reviews", "Reviews", OfferModuleType.REVIEWS),
                    self._module("directions", "Contact and Directions", OfferModuleType.DIRECTIONS),
                    self._module("reminder-ready", "Reminder Ready Structure", OfferModuleType.REMINDERS_READY, optional=True),
                ],
            },
            {
                "category": "barber",
                "slug": "barber-v1",
                "name": "Barber Local Trust Site",
                "status": OfferPlaybookStatus.ACTIVE,
                "package": OfferPackage.LOCAL_TRUST_SITE,
                "description": "Services, prices, booking/contact path, gallery, reviews, and directions.",
                "modules": [
                    self._module("services-prices", "Services and Prices", OfferModuleType.MENU),
                    self._module("booking-request", "Booking Request", OfferModuleType.BOOKING),
                    self._module("gallery", "Haircut Gallery", OfferModuleType.GALLERY),
                    self._module("reviews", "Review Highlights", OfferModuleType.REVIEWS),
                    self._module("directions", "Call and Directions", OfferModuleType.DIRECTIONS),
                ],
            },
            {
                "category": "cleaning_service",
                "slug": "cleaning-service-v1",
                "name": "Cleaning Quote Request Site",
                "status": OfferPlaybookStatus.ACTIVE,
                "package": OfferPackage.QUOTE_REQUEST_SITE,
                "description": "Quote request, service areas, packages, trust, FAQ, and contact.",
                "modules": [
                    self._module("quote-request", "Quote Request", OfferModuleType.QUOTE_REQUEST),
                    self._module("service-area", "Service Area", OfferModuleType.LOCAL_SEO),
                    self._module("packages", "Cleaning Packages", OfferModuleType.CONTENT),
                    self._module("trust-reviews", "Trust and Reviews", OfferModuleType.TRUST),
                    self._module("faq", "FAQ", OfferModuleType.CONTENT),
                ],
            },
            {
                "category": "cafe",
                "slug": "cafe-v1",
                "name": "Cafe Menu QR Site",
                "status": OfferPlaybookStatus.DRAFT,
                "package": OfferPackage.MENU_QR_SITE,
                "description": "Future cafe playbook for editable direct menu and QR menu.",
                "modules": [
                    self._module("editable-menu", "Editable Menu", OfferModuleType.MENU),
                    self._module("qr-menu", "QR Menu", OfferModuleType.MENU),
                    self._module("catering-enquiry", "Catering Enquiry", OfferModuleType.FORMS, optional=True),
                ],
            },
        ]
