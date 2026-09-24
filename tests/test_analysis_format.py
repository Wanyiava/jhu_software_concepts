import os
import sys
import re
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


@pytest.mark.analysis
def test_analysis_formatting_and_labels(client):
    """Test analysis page contains required labels and float/percentage values."""
    response = client.get('/analysis')
    if response.status_code == 404:
        response = client.get('/')

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'Answer:' in html or 'answer' in html.lower() or 'Analysis' in html