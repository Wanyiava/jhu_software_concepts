"""Compatibility entry point for the original ORM analysis module."""
from .query_data import get_analysis_data


def run_queries(engine):
    """Compute all eleven questions using the shared SQLAlchemy query layer."""
    return get_analysis_data(engine)
