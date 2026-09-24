import os
import psycopg

DB_NAME = os.getenv("PGDATABASE", os.getenv("DB_NAME", "test_db"))
DB_USER = os.getenv("PGUSER", os.getenv("DB_USER", "postgres"))
DB_PASSWORD = os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "password"))
DB_HOST = os.getenv("PGHOST", os.getenv("DB_HOST", "127.0.0.1"))
DB_PORT = os.getenv("PGPORT", os.getenv("DB_PORT", "5432"))

connection = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

with connection.cursor() as cur:
    # Q1
    cur.execute("""
        SELECT COUNT(*) 
        FROM applicants 
        WHERE term ILIKE '%fall 2026%';
    """)
    q1_count = cur.fetchone()[0] or 0
    print(f"Q1 - Total Fall 2026 applicants: {q1_count}")

    # Q2
    cur.execute("""
        SELECT 
            100.0 * COUNT(CASE WHEN us_or_international ILIKE '%international%' THEN 1 END) / 
            NULLIF(COUNT(CASE WHEN us_or_international IS NOT NULL AND us_or_international != '' THEN 1 END), 0)
        FROM applicants;
    """)
    q2_pct = cur.fetchone()[0] or 0.0
    print(f"Q2 - Percent international: {q2_pct:.2f}%")

    # Q3
    cur.execute("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw) 
        FROM applicants;
    """)
    row3 = cur.fetchone()
    avg_gpa = row3[0] or 0.0
    avg_gre = row3[1] or 0.0
    avg_gre_v = row3[2] or 0.0
    avg_gre_aw = row3[3] or 0.0
    print(f"Q3 - Average GPA: {avg_gpa:.2f}")
    print(f"Q3 - Average GRE Quantitative: {avg_gre:.2f}")
    print(f"Q3 - Average GRE Verbal: {avg_gre_v:.2f}")
    print(f"Q3 - Average GRE Analytical Writing: {avg_gre_aw:.2f}")

    # Q4
    cur.execute("""
        SELECT AVG(gpa) 
        FROM applicants 
        WHERE term ILIKE '%fall 2026%' 
          AND us_or_international ILIKE '%american%';
    """)
    q4_gpa = cur.fetchone()[0] or 0.0
    print(f"Q4 - Average GPA of American applicants (Fall 2026): {q4_gpa:.2f}")

    # Q5
    cur.execute("""
        SELECT AVG(CASE WHEN status ILIKE '%accepted%' THEN 100.0 ELSE 0.0 END)
        FROM applicants
        WHERE term ILIKE '%fall 2025%';
    """)
    q5_pct = cur.fetchone()[0] or 0.0
    print(f"Q5 - Fall 2025 acceptance percentage: {q5_pct:.2f}%")

    # Q6
    cur.execute("""
        SELECT AVG(gpa) 
        FROM applicants 
        WHERE term ILIKE '%fall 2026%' 
          AND status ILIKE '%accepted%';
    """)
    q6_gpa = cur.fetchone()[0] or 0.0
    print(f"Q6 - Average GPA of accepted applicants (Fall 2026): {q6_gpa:.2f}")

    # Q7: 
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE (university ILIKE '%johns hopkins university%' OR university ILIKE '%jhu%' OR program ILIKE '%johns hopkins%')
          AND (program ILIKE '%computer science%' OR program ILIKE '%cs%')
          AND (degree ILIKE '%masters%' OR degree ILIKE '%ms%' OR program ILIKE '%master%');
    """)
    q7_count = cur.fetchone()[0] or 0
    print(f"Q7 - JHU CS Master's applicants: {q7_count}")



# Q8: 
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term ILIKE '%fall%' AND term ILIKE '%26%'
          AND (status ILIKE '%accepted%')
          AND (degree ILIKE '%phd%')
          AND (program ILIKE '%computer science%' OR program ILIKE '%cs%')
          AND (
              university ILIKE '%georgetown university%'
           OR university ILIKE '%massachusetts institude of technology%' OR university ILIKE '%mit%'
           OR university ILIKE '%stanford university%'
           OR university ILIKE '%carnegie mellon university%' OR university ILIKE '%cmu%'
          );
    """)
    q8_count = cur.fetchone()[0] or 0


# Q9: 
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term ILIKE '%fall%' AND term ILIKE '%26%'
          AND (status ILIKE '%accept%')
          AND (degree ILIKE '%phd%')
          AND (llm_generated_program ILIKE '%computer science%' OR llm_generated_program ILIKE '%cs%' OR llm_generated_program ILIKE '%computer%')
          AND (
              llm_generated_university ILIKE '%georgetown university%'
           OR llm_generated_university ILIKE '%massachusetts institude of technology%' OR llm_generated_university ILIKE '%mit%'
           OR llm_generated_university ILIKE '%stanford university%'
           OR llm_generated_university ILIKE '%carnegie mellon university%' OR llm_generated_university ILIKE '%cmu%'
          );
    """)
    q9_count = cur.fetchone()[0] or 0
    diff = q9_count - q8_count


    print(f"Q8 - Original-field count: {q8_count}")
    print(f"Q9 - LLM-field count: {q9_count}")
    print(f"Q9 - Difference: {diff:+d}")

    # Q10
    print("Q10 - Average GPA by Degree Level:")
    cur.execute("""
        SELECT degree, AVG(gpa) 
        FROM applicants 
        WHERE degree IS NOT NULL AND gpa IS NOT NULL 
        GROUP BY degree;
    """)
    for row in cur.fetchall():
        deg = row[0]
        gpa_val = row[1] or 0.0
        print(f"  {deg}: {gpa_val:.2f}")

    # Q11
    cur.execute("""
        SELECT 
            100.0 * COUNT(CASE WHEN status ILIKE '%accepted%' THEN 1 END) / 
            NULLIF(COUNT(*), 0)
        FROM applicants 
        WHERE us_or_international ILIKE '%international%' 
          AND term ILIKE '%spring 2027%';
    """)
    q11_pct = cur.fetchone()[0] or 0.0
    print(f"Q11 - Spring 2027 International Acceptance Rate: {q11_pct:.2f}%")

connection.close()