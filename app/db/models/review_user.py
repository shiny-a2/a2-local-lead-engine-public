from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReviewUserRole
from app.db.base import Base, TimestampMixin


class ReviewUser(TimestampMixin, Base):
    __tablename__ = "review_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[ReviewUserRole] = mapped_column(Enum(ReviewUserRole, native_enum=False))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
