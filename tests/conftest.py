import os

# Ignore the operator .env during tests so sender/SMTP/OpenAI config there cannot break
# tests that assert safe defaults. Must run before app.settings is imported below.
os.environ["A2_ENV_FILE"] = "tests/.nonexistent-test.env"

import pytest  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import make_engine, make_session_factory  # noqa: E402
from app.settings import Settings  # noqa: E402


@pytest.fixture()
def test_settings(tmp_path):
    return Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", testing=True)


@pytest.fixture()
def session(test_settings):
    engine = make_engine(test_settings)
    Base.metadata.create_all(engine)
    factory = make_session_factory(test_settings)
    with factory() as db:
        yield db

