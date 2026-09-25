# Module 4 — Grad Café Analytics

Flask admissions analytics with a real PostgreSQL test suite and Sphinx documentation. All sixteen original Module 3 columns and eleven analysis questions are retained. Pull Data executes scrape → clean → atomic insert; Update Analysis refreshes the displayed results.

**Repository SSH URL:** `git@github.com:Wanyiava/jhu_software_concepts.git`

**Documentation:** [built HTML](docs/_build/html/index.html) · [source](docs/index.rst) · [publication status](SUBMISSION_CHECKLIST.md). A verified hosted URL must be added after Read the Docs publishes this revision.

## Setup

Use Python 3.12/3.13 and PostgreSQL 16. From the repository root:

```sh
cd module_4
python -m venv .venv
# Activate: source .venv/bin/activate (macOS/Linux)
# Activate: .venv\Scripts\Activate.ps1 (PowerShell)
python -m pip install -r requirements.txt
```

Start an isolated development database (localhost only):

```sh
docker run --name gradcafe-dev -d -p 127.0.0.1:55432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_DB=gradcafe postgres:16-alpine
```

PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe"
$env:TEST_DATABASE_URL = $env:DATABASE_URL
```

macOS/Linux:

```sh
export DATABASE_URL='postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe'
export TEST_DATABASE_URL="$DATABASE_URL"
```

Trust authentication is for this disposable local container only. Shared databases should use authenticated URLs supplied through the environment. Tests require PostgreSQL schema-creation privileges and isolate each case in a temporary UUID schema.

## Run the application

```sh
python -m flask --app src.flask_app:create_app init-db
python -m flask --app src.flask_app:create_app run --port 8080
```

Open [the analysis page](http://127.0.0.1:8080/analysis). Pull Data inserts new URLs and reports the inserted count. Update Analysis refreshes the snapshot. Both return HTTP 409 without work while another operation holds the per-app lock.

Import earlier data with `python -m flask --app src.flask_app:create_app import-data path/to/export.json`. JSON arrays and multi-record JSONL are supported. Initialize a fresh database for historical exports: `init-db` does not migrate existing table constraints or destroy old data. Optional LLM enrichment fields are preserved; they remain NULL if not supplied.

## Tests and coverage

```sh
python -m pytest
python -m pytest -m "web or buttons or analysis or db or integration"
```

Every test has a registered assignment marker. Both commands run the complete suite and enforce **100% statement and branch coverage of all Python code in `module_4/src`**, with no coverage exclusions. Database tests execute real PostgreSQL inserts, uniqueness constraints, queries, and rollback. Network inputs are faked and accidental HTTP is blocked. Busy tests use locks and events, not sleeps. See [coverage_summary.txt](coverage_summary.txt) for actual results.

For a focused development run: `python -m pytest -m buttons --no-cov`. If the system temporary directory is not writable: `python -m pytest --basetemp=.pytest-tmp` (that directory is disposable).

## Sphinx and CI

```sh
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. The handbook includes setup, architecture, all-module autodoc, testing, operations, troubleshooting, and submission instructions.

The [root workflow](../.github/workflows/tests.yml) starts PostgreSQL, runs the full marked suite with coverage, builds documentation, and uploads the results. The [Read the Docs configuration](../.readthedocs.yaml) installs `module_4/requirements.txt` and builds `module_4/docs/conf.py`. Current remote evidence is tracked separately in the [submission checklist](SUBMISSION_CHECKLIST.md).

## Layout

```text
module_4/
  src/                     Flask + ETL + PostgreSQL + templates/static
  tests/                   Required test files, fixtures, extra boundary tests
  docs/                    Sphinx sources and committed _build/html
  pytest.ini               Markers and 100% statement/branch gate
  requirements.txt         Pinned direct dependencies
  coverage_summary.txt     Unedited full-suite terminal output
  README.md
  SUBMISSION_CHECKLIST.md
```

The earlier root source is preserved for provenance; the root pytest configuration selects the current Module 4 tests. Run the single-process application as documented. A multi-worker deployment would require shared job state/locking; the current thread lock is intentionally scoped to this coursework service.
