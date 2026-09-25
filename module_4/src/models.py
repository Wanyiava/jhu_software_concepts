"""The Module 3 applicant schema, with explicit connection configuration."""
import os
from sqlalchemy import Column, Date, Float, Integer, Text, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Applicant(Base):
    """One survey submission; its canonical URL is the uniqueness key.

    All sixteen Module 3 column names and their types are preserved. Unknown
    optional values remain NULL; core identity fields must be present.
    """
    __tablename__ = "applicants"
    p_id = Column(Integer, primary_key=True)
    program = Column(Text, nullable=False)
    university = Column(Text, nullable=False)
    comments = Column(Text)
    date_added = Column(Date, nullable=False)
    url = Column(Text, nullable=False, unique=True)
    status = Column(Text, nullable=False)
    term = Column(Text)
    us_or_international = Column(Text)
    gpa = Column(Float)
    gre = Column(Float)
    gre_v = Column(Float)
    gre_aw = Column(Float)
    degree = Column(Text)
    llm_generated_program = Column(Text)
    llm_generated_university = Column(Text)


def make_engine(database_url=None):
    """Build a lazy PostgreSQL engine from an argument or DATABASE_URL."""
    value = database_url or os.environ.get("DATABASE_URL")
    if not value:
        raise ValueError("Set DATABASE_URL to a PostgreSQL connection URL")
    url = make_url(value)
    if url.drivername == "postgres":
        url = url.set(drivername="postgresql+psycopg2")
    if url.get_backend_name() != "postgresql":
        raise ValueError("DATABASE_URL must use PostgreSQL")
    return create_engine(url, pool_pre_ping=True)


def init_db(engine):
    """Create missing tables; never drop or truncate existing application data."""
    Base.metadata.create_all(engine)
