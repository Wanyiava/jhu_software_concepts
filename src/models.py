import os
from sqlalchemy import create_engine, Column, Integer, Text, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or "@" not in DATABASE_URL:
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "password")
    host = os.getenv("PGHOST", "127.0.0.1")
    port = os.getenv("PGPORT", "5432")
    db = os.getenv("PGDATABASE", "test_db")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Applicant(Base):
    __tablename__ = 'applicants'

    p_id = Column(Integer, primary_key=True)
    program = Column(Text)
    university = Column(Text)
    comments = Column(Text)
    date_added = Column(Date)
    url = Column(Text)
    status = Column(Text)
    term = Column(Text)
    us_or_international = Column(Text)
    gpa = Column(Float)
    gre = Column(Float)
    gre_v = Column(Float)
    gre_aw = Column(Float)
    degree = Column(Text)
    llm_generated_program = Column(Text)
    llm_generated_university = Column(Text)