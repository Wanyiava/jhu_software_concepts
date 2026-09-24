import os
import json
import re
from datetime import datetime
import psycopg

connection = psycopg.connect(
    dbname="studentCourses",
    user="liuwanyi",
    password="",
    host="localhost",
    port="5432"
)

data_list = []
with open('llm_extend_applicant_data.json', 'r', encoding='utf-8') as f:
    try:
        data_list = json.load(f)
    except json.JSONDecodeError:
        f.seek(0)
        for line in f:
            if line.strip():
                data_list.append(json.loads(line.strip()))

def parse_float(val):
    if val is None or isinstance(val, (dict, list)):
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "none", "nan"):
        return None
    match = re.search(r'\d+\.?\d*', val_str)
    return float(match.group(0)) if match else None

def parse_str(val):
    if val is None or isinstance(val, (dict, list)):
        return None
    s = str(val).strip()
    return s if s else None

def parse_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    for fmt in ('%b %d, %Y', '%Y-%m-%d', '%b %d %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            pass
    return None

with connection.cursor() as cur:
    cur.execute("DROP TABLE IF EXISTS applicants;")
    cur.execute("""
        CREATE TABLE applicants (
            p_id INT PRIMARY KEY,
            program TEXT,
            university TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
    """)

    insert_sql = """
        INSERT INTO applicants (
            p_id, program, university, comments, date_added, url, status, term,
            us_or_international, gpa, gre, gre_v, gre_aw, degree,
            llm_generated_program, llm_generated_university
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """

    for idx, item in enumerate(data_list, start=1):
        prog_text = parse_str(item.get('program'))
        univ_text = parse_str(item.get('university'))
        comments_text = parse_str(item.get('comments'))

        gre_val = parse_float(item.get('GRE') or item.get('gre'))
    
        match_v = re.search(r'GRE\s*V\s*(\d+\.?\d*)', comments_text or '', re.IGNORECASE)
        gre_v_val = float(match_v.group(1)) if match_v else None

        match_aw = re.search(r'GRE\s*AW\s*(\d+\.?\d*)', comments_text or '', re.IGNORECASE)
        gre_aw_val = float(match_aw.group(1)) if match_aw else None

        cur.execute(insert_sql, (
            idx,
            prog_text,
            univ_text,
            comments_text,
            parse_date(item.get('date_added')),
            parse_str(item.get('url')),
            parse_str(item.get('status')),
            parse_str(item.get('term')),
            parse_str(item.get('US/International') or item.get('us_or_international')),
            parse_float(item.get('GPA') or item.get('gpa')),
            gre_val,
            gre_v_val,
            gre_aw_val,
            parse_str(item.get('Degree') or item.get('degree')),
            parse_str(item.get('llm-generated-program') or item.get('llm_generated_program')),
            parse_str(item.get('llm-generated-university') or item.get('llm_generated_university'))
        ))

    connection.commit()
    connection.close()
