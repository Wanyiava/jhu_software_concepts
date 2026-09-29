"""Module 3's eleven analysis questions, computed in PostgreSQL."""
from psycopg2 import sql
from sqlalchemy import and_, func, select
from .models import Applicant


def empty_analysis():
    """Return the complete template contract for an empty applicant table."""
    return {"q1": 0, "q2": 0.0,
            "q3": {"gpa": None, "gre": None, "gre_v": None, "gre_aw": None},
            "q4": None, "q5": 0.0, "q6": None, "q7": 0, "q8": 0,
            "q9": 0, "diff": 0, "q10": {}, "q11": 0.0}


def fetch_applicants(engine, limit=100, order_by="p_id"):
    """Return fields as dictionaries, using safe psycopg2.sql composition and enforced LIMIT."""
    safe_limit = max(1, min(int(limit), 100))

    query = sql.SQL(
        "SELECT * FROM {table} ORDER BY {order_col} LIMIT %s"
    ).format(
        table=sql.Identifier("applicants"),
        order_col=sql.Identifier(order_by)
    )

    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cursor:
            cursor.execute(query, (safe_limit,))
            colnames = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(colnames, row)) for row in rows]
    finally:
        raw_conn.close()

def get_analysis_data(engine):
    #pylint: disable=too-many-locals
    """Return numeric q1-q11/diff results; formatting belongs to the template.

    Q2 excludes unknown citizenship. Q5 includes all Fall 2025 decisions; Q11
    includes international Spring 2027 decisions. Empty rates are 0.0; missing
    averages are None. A repeatable-read snapshot keeps all answers consistent.
    """
    a = Applicant
    fall26 = a.term.ilike("%fall 2026%")
    fall25 = a.term.ilike("%fall 2025%")
    accepted = a.status.ilike("accepted%")
    international = a.us_or_international.ilike("%international%")
    spring27 = and_(international, a.term.ilike("%spring 2027%"))
    cs_pattern = r"\m(computer science|cs)\M"
    schools = (
        r"\m(georgetown|massachusetts institute of technology|"
        r"mit|stanford|carnegie mellon|cmu)\M"
    )
    phd = a.degree.op("~*")(r"\m(phd|ph\.?d\.?|doctorate)\M")
    def count(condition):  # pylint: disable=not-callable
        return func.count().filter(condition)  # pylint: disable=not-callable
    def rate(numerator, denominator):
        return func.coalesce(100.0 * count(numerator) / func.nullif(count(denominator), 0), 0.0)
    statement = select(
        count(fall26).label("q1"),
        rate(international, and_(a.us_or_international.isnot(None),
                                 a.us_or_international != "")).label("q2"),
        *(func.avg(getattr(a, key)).label(key) for key in ("gpa", "gre", "gre_v", "gre_aw")),
        func.avg(a.gpa).filter(and_(fall26, a.us_or_international.ilike("%american%"))).label("q4"),
        rate(and_(fall25, accepted), fall25).label("q5"),
        func.avg(a.gpa).filter(and_(fall26, accepted)).label("q6"),
        count(and_(a.university.op("~*")(r"\m(johns hopkins|jhu)\M"),
                   a.program.op("~*")(cs_pattern),
                   a.degree.op("~*")(r"\m(masters?|ms|msc|ma)\M"))).label("q7"),
        count(and_(fall26, accepted, phd, a.program.op("~*")(cs_pattern),
                   a.university.op("~*")(schools))).label("q8"),
        count(and_(fall26, accepted, phd, a.llm_generated_program.op("~*")(cs_pattern),
                   a.llm_generated_university.op("~*")(schools))).label("q9"),
        rate(and_(spring27, accepted), spring27).label("q11"),
    ).select_from(a)
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            result = dict(connection.execute(statement).mappings().one())
            result["q10"] = dict(connection.execute(select(a.degree, func.avg(a.gpa))
                .where(a.degree.isnot(None), a.gpa.isnot(None))
                .group_by(a.degree).order_by(a.degree)).all())
    result["q3"] = {key: result.pop(key) for key in ("gpa", "gre", "gre_v", "gre_aw")}
    for key in ("q2", "q5", "q11"):
        result[key] = float(result[key])
    result["diff"] = result["q9"] - result["q8"]
    return result
