"""Real database end-to-end flows with only the external scraper replaced."""
from copy import deepcopy
import pytest
from bs4 import BeautifulSoup
from src.query_data import fetch_applicants

pytestmark = [pytest.mark.integration, pytest.mark.db]


def test_pull_update_render(engine, db_app, records):
    client = db_app.test_client()
    before = BeautifulSoup(client.get("/analysis").data, "html.parser")
    assert before.select_one('[data-question="1"] .value').text == "0"
    assert client.post("/pull-data").json == {"ok": True, "inserted": 3}
    assert len(fetch_applicants(engine)) == 3
    # Pull persists data; Update Analysis refreshes the displayed snapshot.
    stale = BeautifulSoup(client.get("/analysis").data, "html.parser")
    assert stale.select_one('[data-question="1"] .value').text == "0"
    assert client.post("/update-analysis").json["ok"] is True
    page = BeautifulSoup(client.get("/analysis").data, "html.parser")
    assert page.select_one('[data-question="1"] .value').text == "2"
    assert page.select_one('[data-question="2"] .value').text == "50.00%"
    assert page.select_one('[data-question="5"] .value').text == "100.00%"


def test_overlapping_pulls_keep_unique_results(engine, db_app, records):
    client = db_app.test_client()
    assert client.post("/pull-data").json["inserted"] == 3
    scraper = db_app.extensions["gradcafe"].scraper
    scraper.return_value = [deepcopy(records[1]), dict(records[0], url="https://www.thegradcafe.com/result/2000")]
    assert client.post("/pull-data").json["inserted"] == 1
    assert len(fetch_applicants(engine)) == 4
    assert len({row["url"] for row in fetch_applicants(engine)}) == 4
    result = client.post("/update-analysis").json["results"]
    assert result["q1"] == 3
    page = BeautifulSoup(client.get("/analysis").data, "html.parser")
    assert page.select_one('[data-question="2"] .value').text == "33.33%"
