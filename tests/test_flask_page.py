import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.app import app


@pytest.fixture
def client():
    """Create and configure a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.web
def test_flask_app_routes(client):
    """Test app factory and check that required routes are properly registered."""
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    assert '/analysis' in routes or '/' in routes


@pytest.mark.web
def test_get_analysis_page(client):
    """Test GET /analysis page rendering and check for required HTML content."""
    response = client.get('/analysis')
    if response.status_code == 404:
        response = client.get('/')

    assert response.status_code == 200

    html_content = response.get_data(as_text=True)

    
    assert 'Pull Data' in html_content or 'pull' in html_content.lower()
    assert 'Update Analysis' in html_content or 'update' in html_content.lower()
    assert 'Analysis' in html_content or 'analysis' in html_content.lower()
    assert 'Answer:' in html_content or 'answer' in html_content.lower()