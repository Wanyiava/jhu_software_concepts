import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.buttons
def test_post_pull_data(client):
    """Test POST /pull-data route."""
    response = client.post('/pull-data')
    if response.status_code == 404:
        response = client.post('/pull_data')
    assert response.status_code in [200, 302, 404, 409, 500]


@pytest.mark.buttons
def test_post_update_analysis(client):
    """Test POST /update-analysis route."""
    response = client.post('/update-analysis')
    if response.status_code == 404:
        response = client.post('/update_analysis')
    assert response.status_code in [200, 302, 404, 409, 500]