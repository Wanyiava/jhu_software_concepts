"""Scraper, cleaning, import, and configuration boundary tests."""
import json
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock
import pytest
import requests
from src import scrape
from src.app import create_app
from src.clean import canonical_url, clean_data, parse_date, parse_float, parse_str
from src.load_data import read_records
from src.models import make_engine
from src.orm_queries import run_queries
from src.query_data import empty_analysis, fetch_applicants

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("value,expected", [(None, None), ({}, None), ([], None),
    ("", None), (" null ", None), ("None", None), ("nan", None), ("  CS  ", "CS"), (0, "0")])
def test_parse_str(value, expected):
    assert parse_str(value) == expected


@pytest.mark.parametrize("value,expected", [(None, None), ("nan", None), ("missing", None),
    ("GPA 3.85", 3.85), (0, 0.0), ("-2.5", -2.5), ("1e9999", None)])
def test_parse_float(value, expected):
    assert parse_float(value) == expected


@pytest.mark.parametrize("value,expected", [(None, None), (32, None), ("invalid", None),
    ("2026-01-10", date(2026, 1, 10)), ("Jan 10, 2026", date(2026, 1, 10)),
    ("Jan 10 2026", date(2026, 1, 10)), ("January 10, 2026", date(2026, 1, 10)),
    (date(2026, 1, 10), date(2026, 1, 10)), (datetime(2026, 1, 10, 8), date(2026, 1, 10))])
def test_parse_date(value, expected):
    assert parse_date(value) == expected


@pytest.mark.parametrize("url", [None, "", "/result/1", "ftp://example.org/result/1", "https:///missing"])
def test_invalid_identity_urls(url):
    with pytest.raises(ValueError, match="absolute HTTP"):
        canonical_url(url)


def test_url_normalization_retains_result_identity():
    assert canonical_url(" HTTPS://EXAMPLE.ORG/result/1/#comment ") == "https://example.org/result/1"
    assert canonical_url("https://example.org/result.php?id=9") != canonical_url("https://example.org/result.php?id=8")


def test_clean_legacy_aliases_and_comment_scores(records):
    row = dict(records[0])
    for key in ("gpa", "gre", "gre_v", "gre_aw", "degree", "us_or_international",
                "llm_generated_program", "llm_generated_university"):
        row.pop(key)
    row.update({"GPA": "GPA 3.8", "GRE": "GRE 167", "Degree": "Masters",
                "US/International": "International", "comments": "GRE V 159 GRE AW: 4.0",
                "llm-generated-program": "CS", "llm-generated-university": "Stanford"})
    cleaned = clean_data([row])[0]
    assert cleaned["gpa"] == 3.8 and cleaned["gre"] == 167.0
    assert cleaned["gre_v"] == 159.0 and cleaned["gre_aw"] == 4.0
    assert cleaned["degree"] == "Masters" and cleaned["us_or_international"] == "International"
    assert cleaned["llm_generated_program"] == "CS"
    assert cleaned["llm_generated_university"] == "Stanford"
    assert "GPA" in row and "gpa" not in row  # Caller data stays unchanged.


def test_optional_enrichment_and_zero_scores(records):
    result = clean_data([dict(records[0], gpa=0, comments=None, gre_v=None, gre_aw=None)],
                        enrich=lambda row: {"llm_generated_program": "Enriched"})[0]
    assert result["gpa"] == 0.0 and result["gre_v"] is None
    assert result["llm_generated_program"] == "Enriched"


@pytest.mark.parametrize("key", ["program", "university", "date_added", "status"])
def test_missing_core_fields_are_rejected(records, key):
    with pytest.raises(ValueError, match=key):
        clean_data([dict(records[0], **{key: None})])


@pytest.mark.parametrize("body,expected", [('[]', []), ('[{"x":1}]', [{"x": 1}]),
    ('{"x":1}\n\n{"x":2}\n', [{"x": 1}, {"x": 2}]), ("", [])])
def test_json_and_jsonl_reading(tmp_path, body, expected):
    file = tmp_path / "input.json"
    file.write_text(body, encoding="utf-8")
    assert read_records(file) == expected


@pytest.mark.parametrize("body", ['{"not": "an array"}', '[1]', '42', 'bad JSON'])
def test_invalid_imports_are_rejected(tmp_path, body):
    file = tmp_path / "bad.json"
    file.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError):
        read_records(file)


@pytest.mark.parametrize("pages", [0, 11, -1, True, 1.5, "2"])
def test_scrape_page_limits(pages):
    with pytest.raises(ValueError, match="between 1 and 10"):
        scrape._build_urls(pages)


def test_parse_html_has_no_cross_record_detail_leakage():
    html = (Path(__file__).parent / "fixtures" / "survey.html").read_text(encoding="utf-8")
    rows = scrape._parse_html(html)
    assert len(rows) == 4
    assert rows[0]["degree"] == "PhD"
    assert rows[0]["gpa"] == "3.9" and rows[0]["gre"] == "165"
    assert rows[0]["url"] == "https://www.thegradcafe.com/result/1001"
    assert rows[0]["us_or_international"] == "American"
    assert rows[1]["comments"] == "" and rows[1]["term"] is None
    assert rows[2]["degree"] == "Masters" and rows[2]["term"] == "Spring 2027"
    assert rows[3]["url"] == "" and rows[3]["comments"] == ""


def test_bounded_scraper_stops_at_empty_page():
    html = '<table><tr><td>U</td><td>CS PhD</td><td>Jan 10, 2026</td><td>Accepted</td><td><a href="/result/1">View</a></td></tr></table>'
    first, empty = Mock(text=html), Mock(text="<table></table>")
    get = Mock(side_effect=[first, empty])
    assert len(scrape.scrape_data(3, http_get=get)) == 1
    assert get.call_count == 2
    assert get.call_args_list[0].args == (scrape.BASE_URL + "?p=1",)
    assert get.call_args.kwargs["timeout"] == 15
    first.raise_for_status.assert_called_once_with()
    all_pages = Mock(return_value=first)
    assert len(scrape.scrape_data(2, http_get=all_pages)) == 2
    assert all_pages.call_count == 2


def test_default_scraper_transport_and_http_error(monkeypatch):
    response = Mock(text="<table></table>")
    get = Mock(return_value=response)
    monkeypatch.setattr(scrape.requests, "get", get)
    assert scrape.scrape_data() == []
    response.raise_for_status.side_effect = requests.HTTPError("unavailable")
    with pytest.raises(requests.HTTPError):
        scrape.scrape_data()
    get.side_effect = requests.Timeout("timeout")
    with pytest.raises(requests.Timeout):
        scrape.scrape_data()


def test_scrape_helpers_roundtrip(tmp_path):
    file = tmp_path / "records.json"
    data = [{"program": "Café studies"}]
    scrape.save_data(data, file)
    assert scrape.load_data(file) == data


def test_engine_configuration_is_explicit(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="Set DATABASE_URL"):
        make_engine()
    with pytest.raises(ValueError, match="must use PostgreSQL"):
        make_engine("sqlite://")
    monkeypatch.setenv("DATABASE_URL", "postgres://user@localhost/example")
    engine = make_engine()
    assert engine.url.drivername == "postgresql+psycopg2"
    engine.dispose()
    engine = make_engine("postgresql+psycopg2://override@localhost/other")
    assert engine.url.username == "override"
    engine.dispose()


@pytest.mark.db
def test_factory_default_dependencies_and_import_cli(engine, tmp_path, records, monkeypatch):
    import src.flask_app as web
    monkeypatch.setattr(web, "make_engine", Mock(return_value=engine))
    monkeypatch.setattr(web, "scrape_data", Mock(return_value=[]))
    app = create_app({"TESTING": True, "SCRAPE_PAGES": 2, "DATABASE_URL": "configured"})
    web.make_engine.assert_called_once_with("configured")
    assert app.test_client().post("/pull-data").json["inserted"] == 0
    web.scrape_data.assert_called_once_with(2)
    file = tmp_path / "rows.json"
    file.write_text(json.dumps(records, default=str), encoding="utf-8")
    result = app.test_cli_runner().invoke(args=["import-data", str(file)])
    assert result.exit_code == 0 and "Inserted 3" in result.output
    assert len(fetch_applicants(engine)) == 3


@pytest.mark.db
def test_orm_compatibility_entry_point(engine):
    assert run_queries(engine) == empty_analysis()
