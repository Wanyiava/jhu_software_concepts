"""Transactional and idempotent inserts into the original applicant table."""
import json
from pathlib import Path
from sqlalchemy.dialects.postgresql import insert
from .models import Applicant


def read_records(filename):
    """Read a JSON array or newline-delimited JSON exported by Module 2/3."""
    content = Path(filename).read_text(encoding="utf-8")
    try:
        records = json.loads(content)
    except json.JSONDecodeError:
        records = [json.loads(line) for line in content.splitlines() if line.strip()]
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise ValueError("Input must contain a JSON array or JSONL applicant objects")
    return records


def load_data(records, engine):
    """Insert a batch atomically; return the count of new source URLs.

    PostgreSQL enforces URL uniqueness even with concurrent writers. Any failed
    insert rolls back the entire batch; duplicates leave the existing row intact.
    Records must already be normalized by :func:`src.clean.clean_data`.
    """
    inserted = 0
    with engine.begin() as connection:
        for record in records:
            statement = (insert(Applicant).values(**record)
                         .on_conflict_do_nothing(index_elements=["url"])
                         .returning(Applicant.p_id))
            inserted += connection.execute(statement).scalar_one_or_none() is not None
    return inserted
