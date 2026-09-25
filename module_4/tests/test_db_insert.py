"""Real PostgreSQL constraints, query contracts, and transactional rollback."""
from datetime import date
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from src.models import Applicant
from src.load_data import load_data
from src.query_data import fetch_applicants, get_analysis_data

pytestmark = pytest.mark.db

FIELDS = {"p_id", "program", "university", "comments", "date_added", "url",
          "status", "term", "us_or_international", "gpa", "gre", "gre_v",
          "gre_aw", "degree", "llm_generated_program", "llm_generated_university"}


def test_pull_inserts_required_schema_and_values(engine, db_app, records):
    assert fetch_applicants(engine) == []
    response = db_app.test_client().post("/pull-data")
    assert response.status_code == 200 and response.json["inserted"] == 3
    rows = fetch_applicants(engine)
    assert len(rows) == 3
    for actual, expected in zip(rows, records):
        assert set(actual) == FIELDS
        assert actual["p_id"] > 0
        for key, value in expected.items():
            assert actual[key] == value
        assert all(actual[key] is not None for key in
                   ("p_id", "program", "university", "date_added", "url", "status"))
    columns = {column["name"]: column for column in inspect(engine).get_columns("applicants")}
    assert set(columns) == FIELDS
    assert not columns["url"]["nullable"] and columns["gpa"]["nullable"]


def test_duplicate_pull_is_idempotent(engine, db_app):
    client = db_app.test_client()
    assert client.post("/pull-data").json["inserted"] == 3
    assert client.post("/pull-data").json["inserted"] == 0
    assert len(fetch_applicants(engine)) == 3


def test_empty_batch(engine):
    assert load_data([], engine) == 0
    assert fetch_applicants(engine) == []


def test_postgres_unique_constraint(engine, records):
    load_data(records[:1], engine)
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(Applicant.__table__.insert().values(**records[0]))
    assert len(fetch_applicants(engine)) == 1


def test_failed_batch_rolls_back_all_rows(engine, records):
    broken = dict(records[1], program=None)
    with pytest.raises(IntegrityError):
        load_data([records[0], broken], engine)
    assert fetch_applicants(engine) == []


def test_loader_failure_through_route_leaves_no_partial_writes(engine, records):
    from src.flask_app import create_app
    app = create_app({"TESTING": True}, engine=engine,
                     scraper=lambda: [records[0], dict(records[1], status=None)],
                     cleaner=lambda rows: rows)
    response = app.test_client().post("/pull-data")
    assert response.status_code == 500
    assert fetch_applicants(engine) == []
    assert not app.extensions["gradcafe"].lock.locked()


def test_query_contract_and_known_answers(engine, records):
    load_data(records, engine)
    result = get_analysis_data(engine)
    assert set(result) == {*(f"q{i}" for i in range(1, 12)), "diff"}
    assert result["q1"] == 2
    assert result["q2"] == 50.0
    assert result["q3"] == {"gpa": 3.7, "gre": 165.0, "gre_v": 160.0, "gre_aw": 4.5}
    assert result["q4"] == 3.9 and result["q5"] == 100.0
    assert result["q6"] == 3.9 and result["q7"] == 0
    assert result["q8"] == result["q9"] == 1 and result["diff"] == 0
    assert result["q10"] == {"PhD": 3.7} and result["q11"] == 0.0


def test_empty_queries(engine):
    from src.query_data import empty_analysis
    assert get_analysis_data(engine) == empty_analysis()


@pytest.mark.analysis
def test_query_cohorts_and_raw_vs_enriched_names(engine, records):
    base = records[0]
    variants = [
        dict(base, url="https://example.org/1", university="Johns Hopkins University", degree="Masters"),
        dict(base, url="https://example.org/2", university="JHU", program="CS", degree="MS"),
        dict(base, url="https://example.org/3", university="Smith University", program="Physics"),
        dict(base, url="https://example.org/4", status="Not accepted"),
        dict(base, url="https://example.org/5", term="Fall 2025", status="Accepted"),
        dict(base, url="https://example.org/6", term="Fall 2025", status="Rejected"),
        dict(base, url="https://example.org/7", term="Fall 2025", status="Wait listed"),
        dict(base, url="https://example.org/8", term="Spring 2027", us_or_international="International"),
        dict(base, url="https://example.org/9", term="Spring 2027", us_or_international="International", status="Rejected"),
        dict(base, url="https://example.org/10", term="Spring 2027", us_or_international="International"),
    ]
    load_data(variants, engine)
    result = get_analysis_data(engine)
    assert result["q1"] == 4 and result["q7"] == 2
    # Physics at Smith must not match CS at MIT through substrings.
    assert result["q8"] == 0 and result["q9"] == 1 and result["diff"] == 1
    assert result["q5"] == pytest.approx(100 / 3)
    assert result["q11"] == pytest.approx(200 / 3)
    assert result["q2"] == 30.0
