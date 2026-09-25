"""Factory, routes, controls, CLI, and HTML tests."""
import pytest
from bs4 import BeautifulSoup
from src.flask_app import create_app

pytestmark = pytest.mark.web


def test_factory_config_and_isolation(dependencies):
    first = create_app({"TESTING": True, "CUSTOM": "value"}, **dependencies)
    second = create_app(**dependencies)
    assert first.testing and first.config["CUSTOM"] == "value"
    assert not second.testing
    assert first.extensions["gradcafe"] is not second.extensions["gradcafe"]
    assert {rule.rule for rule in first.url_map.iter_rules()} == {
        "/", "/analysis", "/pull-data", "/update-analysis", "/static/<path:filename>"}


@pytest.mark.parametrize("path", ["/", "/analysis"])
def test_analysis_page(client, path):
    response = client.get(path)
    assert response.status_code == 200
    page = BeautifulSoup(response.data, "html.parser")
    assert page.h1.get_text(strip=True) == "Analysis"
    assert "Analysis" in page.title.text
    for name, endpoint, label in [("pull-data", "/pull-data", "Pull Data"),
                                   ("update-analysis", "/update-analysis", "Update Analysis")]:
        button = page.select_one(f'[data-testid="{name}-btn"]')
        assert button.name == "button" and button.text.strip() == label
        assert button.parent["action"] == endpoint
        assert button.parent["method"].lower() == "post"
    assert len(page.select('[data-testid="analysis-answer"]')) == 11


@pytest.mark.parametrize("path", ["/pull-data", "/update-analysis"])
def test_post_routes_reject_get(client, path):
    assert client.get(path).status_code == 405


def test_static_and_missing_routes(client):
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/not-a-route").status_code == 404


def test_html_escapes_database_values(client, dependencies):
    dependencies["query"].return_value["q10"] = {"<script>alert(1)</script>": 3.5}
    html = client.get("/analysis").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)</script>" not in html


def test_page_database_failure_is_safe(client, dependencies):
    dependencies["query"].side_effect = RuntimeError("private connection details")
    response = client.get("/analysis")
    assert response.status_code == 503
    assert "private connection details" not in response.text


@pytest.mark.db
def test_init_db_command(engine, dependencies):
    app = create_app({"TESTING": True}, engine=engine, **dependencies)
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "initialized" in result.output
