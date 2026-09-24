import os
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5432/test_db")
os.environ.setdefault("PGPASSWORD", "password")
os.environ.setdefault("PGUSER", "postgres")
os.environ.setdefault("PGHOST", "127.0.0.1")
import subprocess
from flask import Flask, render_template, request, jsonify
from sqlalchemy import select, func, and_, or_
from src.models import SessionLocal, Applicant

scraping_process = None

def get_analysis_data():
    session = SessionLocal()
    try:
        q1_stmt = select(func.count()).where(and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%26%')))
        q1_val = session.scalar(q1_stmt) or 0

        q4_stmt = select(func.avg(Applicant.gpa)).where(
            and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%26%'), 
                 Applicant.us_or_international.ilike('%american%'), Applicant.gpa.isnot(None))
        )
        q4_val = f"{session.scalar(q4_stmt) or 0.0:.2f}"

        t25 = session.scalar(select(func.count()).where(and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%25%')))) or 0
        a25 = session.scalar(select(func.count()).where(and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%25%'), Applicant.status.ilike('%accepted%')))) or 0
        q5_val = f"{(100.0 * a25 / t25) if t25 > 0 else 0.0:.2f}"

        q8_stmt = select(func.count()).where(
            and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%26%'),
                 Applicant.status.ilike('%accepted%'), Applicant.degree.ilike('%phd%'),
                 or_(Applicant.program.ilike('%computer science%'), Applicant.program.ilike('%cs%')),
                 or_(Applicant.university.ilike('%georgetown%'), Applicant.university.ilike('%massachusetts%'), Applicant.university.ilike('%mit%'), Applicant.university.ilike('%stanford%'), Applicant.university.ilike('%carnegie%'), Applicant.university.ilike('%cmu%')))
        )
        q8_val = session.scalar(q8_stmt) or 0

        q9_stmt = select(func.count()).where(
            and_(Applicant.term.ilike('%fall%'), Applicant.term.ilike('%26%'),
                 Applicant.status.ilike('%accepted%'), Applicant.degree.ilike('%phd%'),
                 or_(Applicant.llm_generated_program.ilike('%computer science%'), Applicant.llm_generated_program.ilike('%cs%')),
                 or_(Applicant.llm_generated_university.ilike('%georgetown%'), Applicant.llm_generated_university.ilike('%massachusetts%'), Applicant.llm_generated_university.ilike('%mit%'), Applicant.llm_generated_university.ilike('%stanford%'), Applicant.llm_generated_university.ilike('%carnegie%'), Applicant.llm_generated_university.ilike('%cmu%')))
        )
        q9_val = session.scalar(q9_stmt) or 0
        diff_val = f"{q9_val - q8_val:+d}"

        q10_stmt = select(Applicant.degree, func.avg(Applicant.gpa)).where(and_(Applicant.degree.isnot(None), Applicant.gpa.isnot(None))).group_by(Applicant.degree)
        q10_val = {deg: f"{gpa or 0.0:.2f}" for deg, gpa in session.execute(q10_stmt)}

        t11 = session.scalar(select(func.count()).where(and_(Applicant.us_or_international.ilike('%international%'), Applicant.term.ilike('%spring 2027%')))) or 0
        a11 = session.scalar(select(func.count()).where(and_(Applicant.us_or_international.ilike('%international%'), Applicant.term.ilike('%spring 2027%'), Applicant.status.ilike('%accepted%')))) or 0
        q11_val = f"{(100.0 * a11 / t11) if t11 > 0 else 0.0:.2f}"

        return {
            'q1': q1_val, 'q4': q4_val, 'q5': q5_val, 'q8': q8_val,
            'q9': q9_val, 'diff': diff_val, 'q10': q10_val, 'q11': q11_val
        }
    finally:
        session.close()


def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)

    @app.route('/')
    @app.route('/analysis')
    def index():
        results = get_analysis_data()
        return render_template('index.html', results=results, message=None)

    @app.route('/pull-data', methods=['POST'])
    def pull_data():
        global scraping_process
        
        if scraping_process is not None and scraping_process.poll() is None:
            return jsonify({"busy": True, "message": "A data pull process is already running."}), 409

        scraping_process = subprocess.Popen(['python3', 'src/scrape.py'])
        return jsonify({"ok": True, "message": "Data pull started successfully!"}), 200

    @app.route('/update-analysis', methods=['POST'])
    def update_analysis():
        global scraping_process
        
        if scraping_process is not None and scraping_process.poll() is None:
            return jsonify({"busy": True, "message": "A background data pull is currently retrieving new entries."}), 409

        results = get_analysis_data()
        return jsonify({"ok": True, "results": results}), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)