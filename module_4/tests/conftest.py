"""Deterministic fixtures; database tests use isolated real PostgreSQL schemas."""
import os
from copy import deepcopy
from datetime import date
from uuid import uuid4
from unittest.mock import Mock

import pytest
import requests
from sqlalchemy import create_engine, text

from src.flask_app import create_app
from src.models import Base
from src.query_data import empty_analysis


def pytest_collection_modifyitems(items):
    """Fail collection if a test lacks an assignment marker."""
    required = {"web", "buttons", "analysis", "db", "integration"}
    unmarked = [item.nodeid for item in items
                if not required.intersection(mark.name for mark in item.iter_markers())]
    if unmarked:
        raise pytest.UsageError("Unmarked tests: " + ", ".join(unmarked))


@pytest.fixture(autouse=True)
def no_live_http(monkeypatch):
    """Tests must explicitly supply an HTTP double; accidental requests fail."""
    def blocked(*args, **kwargs):
        raise AssertionError("Live HTTP is forbidden in the test suite")
    monkeypatch.setattr(requests.sessions.Session, "request", blocked)


@pytest.fixture
def records():
    """Independent, synthetic records in the original Module 3 schema."""
    base = dict(program="Computer Science", university="Stanford University",
                comments="Synthetic fixture", date_added=date(2026, 1, 10),
                status="Accepted", term="Fall 2026", us_or_international="American",
                gpa=3.9, gre=165.0, gre_v=160.0, gre_aw=4.5, degree="PhD",
                llm_generated_program="Computer Science",
                llm_generated_university="Stanford University")
    return [dict(base, url="https://www.thegradcafe.com/result/1001"),
            dict(base, url="https://www.thegradcafe.com/result/1002", gpa=3.5,
                 us_or_international="International", status="Rejected"),
            dict(base, url="https://www.thegradcafe.com/result/1003", gpa=None,
                 term="Fall 2025", us_or_international=None)]


@pytest.fixture
def dependencies(records):
    return {"scraper": Mock(return_value=deepcopy(records)),
            "cleaner": Mock(side_effect=lambda rows: rows),
            "loader": Mock(return_value=len(records)),
            "query": Mock(return_value=empty_analysis())}


@pytest.fixture
def app(dependencies):
    return create_app({"TESTING": True}, **dependencies)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def engine():
    """Create/drop only a UUID schema; never touch existing application tables."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail("Set TEST_DATABASE_URL to a dedicated PostgreSQL test database")
    admin = create_engine(url)
    if admin.dialect.name != "postgresql":
        admin.dispose()
        pytest.fail("Database tests require real PostgreSQL, not SQLite")
    schema = "test_" + uuid4().hex
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        Base.metadata.create_all(scoped)
        yield scoped
    finally:
        scoped.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def db_app(engine, records):
    return create_app({"TESTING": True}, engine=engine,
                      scraper=Mock(return_value=deepcopy(records)))
