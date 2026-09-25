"""Observable busy state and actual dependency calls, without sleeps."""
from threading import Event, Thread
from unittest.mock import Mock
import pytest

pytestmark = pytest.mark.buttons


def test_pull_calls_each_etl_stage(client, dependencies):
    response = client.post("/pull-data")
    assert response.status_code == 200
    assert response.json == {"ok": True, "inserted": 3}
    dependencies["scraper"].assert_called_once_with()
    dependencies["cleaner"].assert_called_once_with(dependencies["scraper"].return_value)
    dependencies["loader"].assert_called_once_with(dependencies["scraper"].return_value)
    dependencies["query"].assert_not_called()


def test_update_refreshes_snapshot(client, dependencies):
    client.get("/analysis")
    dependencies["query"].return_value = dict(dependencies["query"].return_value, q1=42)
    response = client.post("/update-analysis")
    assert response.status_code == 200 and response.json["ok"] is True
    assert response.json["results"]["q1"] == 42
    assert dependencies["query"].call_count == 2
    assert b"42" in client.get("/analysis").data
    assert dependencies["query"].call_count == 2


@pytest.mark.parametrize("endpoint", ["/pull-data", "/update-analysis"])
def test_busy_does_no_work(app, client, dependencies, endpoint):
    state = app.extensions["gradcafe"]
    state.lock.acquire()
    try:
        response = client.post(endpoint)
    finally:
        state.lock.release()
    assert response.status_code == 409 and response.json == {"busy": True}
    for dependency in dependencies.values():
        dependency.assert_not_called()


@pytest.mark.parametrize("stage", ["scraper", "cleaner", "loader"])
def test_pull_failure_releases_busy_gate(app, client, dependencies, stage):
    dependencies[stage].side_effect = RuntimeError("private error")
    response = client.post("/pull-data")
    assert response.status_code == 500 and response.json["ok"] is False
    assert "private error" not in response.text
    assert not app.extensions["gradcafe"].lock.locked()
    if stage != "loader":
        dependencies["loader"].assert_not_called()
    dependencies[stage].side_effect = None
    assert client.post("/pull-data").status_code == 200


def test_update_failure_preserves_previous_snapshot(app, client, dependencies):
    client.get("/analysis")
    old = app.extensions["gradcafe"].analysis.copy()
    dependencies["query"].side_effect = RuntimeError("private error")
    assert client.post("/update-analysis").status_code == 500
    assert app.extensions["gradcafe"].analysis == old
    assert not app.extensions["gradcafe"].lock.locked()


def test_real_in_flight_pull_blocks_both_buttons(app, dependencies):
    started, release = Event(), Event()
    def scraper():
        started.set()
        assert release.wait(timeout=10), "Test failed to release scraper"
        return []
    dependencies["scraper"].side_effect = scraper
    responses = []
    worker = Thread(target=lambda: responses.append(app.test_client().post("/pull-data")))
    worker.start()
    try:
        assert started.wait(timeout=10)
        with app.test_client() as client:
            assert client.post("/pull-data").status_code == 409
            assert client.post("/update-analysis").status_code == 409
            assert client.get("/analysis").status_code == 409
        dependencies["query"].assert_not_called()
    finally:
        release.set()
        worker.join(timeout=10)
    assert not worker.is_alive() and responses[0].status_code == 200


def test_cached_page_remains_available_while_busy(app, client):
    client.get("/analysis")
    state = app.extensions["gradcafe"]
    state.lock.acquire()
    try:
        assert client.get("/analysis").status_code == 200
    finally:
        state.lock.release()
