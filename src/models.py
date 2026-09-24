from sqlalchemy import create_engine, Column, Integer, Text, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://liuwanyi:@localhost:5432/studentCourses"

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