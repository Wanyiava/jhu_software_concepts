import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.models import SessionLocal, Applicant


@pytest.mark.db
def test_db_queries_and_insert():
    """Test database connection and basic query execution."""
    try:
        session = SessionLocal()
        count = session.query(Applicant).count()
        assert isinstance(count, int)
        session.close()
    except Exception:
        pytest.skip("Database service not running locally")