from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import Settings, get_settings


def make_engine(settings: Settings | None = None):
    resolved = settings or get_settings()
    connect_args = (
        {"check_same_thread": False} if resolved.database_url.startswith("sqlite") else {}
    )
    return create_engine(resolved.database_url, future=True, connect_args=connect_args)


def make_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=make_engine(settings), autoflush=False, expire_on_commit=False)


SessionLocal = make_session_factory()


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
