from sqlalchemy import select, func, and_, or_
from src.models import SessionLocal, Applicant
session = SessionLocal()

try:
    # Q1
    stmt1 = select(func.count()).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%26%')
        )
    )
    q1_count = session.scalar(stmt1) or 0
    print(f"Q1 - Total Fall 2026 applicants: {q1_count}")

   
    # Q4: 
    stmt4 = select(func.avg(Applicant.gpa)).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%26%'),
            Applicant.us_or_international.ilike('%american%'),
            Applicant.gpa.isnot(None)
        )
    )
    q4_gpa = session.scalar(stmt4) or 0.0
    print(f"Q4 - Average GPA of American applicants (Fall 2026): {q4_gpa:.2f}")

    # Q5: 
    total_f25_stmt = select(func.count()).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%25%')
        )
    )
    accepted_f25_stmt = select(func.count()).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%25%'),
            Applicant.status.ilike('%accepted%')
        )
    )
    total_f25 = session.scalar(total_f25_stmt) or 0
    accepted_f25 = session.scalar(accepted_f25_stmt) or 0
    q5_pct = (100.0 * accepted_f25 / total_f25) if total_f25 > 0 else 0.0
    print(f"Q5 - Fall 2025 acceptance percentage: {q5_pct:.2f}%")

    
    # Q8:
    stmt8 = select(func.count()).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%26%'),
            Applicant.status.ilike('%accepted%'),
            Applicant.degree.ilike('%phd%'),
            or_(Applicant.program.ilike('%computer science%'), Applicant.program.ilike('%cs%')),
            or_(
                Applicant.university.ilike('%georgetown university%'),
                Applicant.university.ilike('%massachusetts institute of technology%'),
                Applicant.university.ilike('%mit%'),
                Applicant.university.ilike('%stanford university%'),
                Applicant.university.ilike('%carnegie mellon university%'),
                Applicant.university.ilike('%cmu%')
            )
        )
    )
    q8_count = session.scalar(stmt8) or 0
    print(f"Q8 - Original-field count: {q8_count}")

    # Q9: 
    stmt9 = select(func.count()).where(
        and_(
            Applicant.term.ilike('%fall%'),
            Applicant.term.ilike('%26%'),
            Applicant.status.ilike('%accepted%'),
            Applicant.degree.ilike('%phd%'),
            or_(
                Applicant.llm_generated_program.ilike('%computer science%'),
                Applicant.llm_generated_program.ilike('%cs%'),
                Applicant.llm_generated_program.ilike('%computer%')
            ),
            or_(
                Applicant.llm_generated_university.ilike('%georgetown university%'),
                Applicant.llm_generated_university.ilike('%massachusetts institute of technology%'),
                Applicant.llm_generated_university.ilike('%mit%'),
                Applicant.llm_generated_university.ilike('%stanford university%'),
                Applicant.llm_generated_university.ilike('%carnegie mellon university%'),
                Applicant.llm_generated_university.ilike('%cmu%')
            )
        )
    )
    q9_count = session.scalar(stmt9) or 0
    diff = q9_count - q8_count
    print(f"Q9 - LLM-field count: {q9_count}")
    print(f"Q9 - Difference: {diff:+d}")

    # Q10 
    print("Q10 - Average GPA by Degree Level:")
    stmt10 = (
        select(Applicant.degree, func.avg(Applicant.gpa))
        .where(and_(Applicant.degree.isnot(None), Applicant.gpa.isnot(None)))
        .group_by(Applicant.degree)
    )
    for deg, avg_gpa in session.execute(stmt10):
        gpa_val = avg_gpa or 0.0
        print(f"  {deg}: {gpa_val:.2f}")

finally:
  
    session.close()