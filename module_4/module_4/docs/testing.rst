Testing guide
=============

Run the complete suite
----------------------

Set ``TEST_DATABASE_URL`` as described in :doc:`setup`. From ``module_4``:

.. code-block:: console

   python -m pytest
   python -m pytest -m "web or buttons or analysis or db or integration"

Both commands collect the same complete suite. ``pytest.ini`` enables strict
marker validation, all-module coverage, branch coverage, and a 100 percent
threshold. The collection hook rejects unmarked tests. No tests are skipped
when PostgreSQL is missing: database fixtures fail with a configuration error.

To focus on a category during development, disable the full-suite coverage
threshold for that focused run only:

.. code-block:: console

   python -m pytest -m buttons --no-cov
   python -m pytest -m db --no-cov

.. list-table:: Required markers and files
   :header-rows: 1
   :widths: 20 40 40

   * - Marker
     - Primary file
     - Verification
   * - ``web``
     - ``test_flask_page.py``
     - Factory, configuration, all routes, HTML, CLI, escaping.
   * - ``buttons``
     - ``test_buttons.py``
     - ETL calls, busy rejection, cache refresh, failure recovery.
   * - ``analysis``
     - ``test_analysis_format.py``
     - Every answer label and every two-decimal percentage.
   * - ``db``
     - ``test_db_insert.py``
     - Real PostgreSQL schema, insert/select, constraints, rollback, aggregates.
   * - ``integration``
     - ``test_integration_end_to_end.py``
     - Pull → update → render and overlapping pulls.
   * - ``integration`` (and ``db`` where needed)
     - ``test_data_modules.py``
     - Parser, cleaning, configuration, import/export, default dependency paths.

Fixtures and doubles
--------------------

``records`` provides independent, synthetic Module 3 records. ``dependencies``
provides call-observable scraper/cleaner/loader/query doubles for web unit tests.
``db_app`` replaces only the external scraper; real cleaning, insertion,
aggregation, and rendering execute during integration tests.

Each ``engine`` fixture creates a UUID-named PostgreSQL schema, directs its
connections to that schema, then drops only that schema and disposes connections.
It never truncates application tables. The test role needs schema-creation
permissions in a disposable database. SQLite and in-memory list substitutes
are not used for database assertions.

An autouse fixture blocks accidental ``requests`` traffic. Scraper tests pass a
fake HTTP getter or replace ``requests.get`` explicitly and use checked-in HTML.
No tests launch a subprocess scraper, contact Grad Café, or download a model.

Busy-state tests either acquire the exposed lock directly or coordinate a real
in-flight request with ``threading.Event``. Events have timeout bounds for failed
tests, but there are no arbitrary sleeps or timing assumptions.

Stable selectors
----------------

.. code-block:: text

   [data-testid="pull-data-btn"]
   [data-testid="update-analysis-btn"]
   [data-testid="analysis-answer"]
   [data-testid="percentage"]
   [data-question="1"] ... [data-question="11"]

BeautifulSoup verifies elements, form methods/actions, all labels, and all
percentages with ``\d+\.\d{2}%``. Flask's test client exercises requests; manual
browser interaction is not required to run any test.

Coverage evidence and CI
------------------------

PowerShell:

.. code-block:: powershell

   python -m pytest -m "web or buttons or analysis or db or integration" | Tee-Object coverage_summary.txt
   if ($LASTEXITCODE -ne 0) { throw "Tests failed" }

macOS/Linux:

.. code-block:: bash

   set -o pipefail
   python -m pytest -m "web or buttons or analysis or db or integration" | tee coverage_summary.txt

The repository-root ``.github/workflows/tests.yml`` starts PostgreSQL 16, installs
pinned dependencies, runs the marked suite with coverage, builds Sphinx with
warnings treated as errors, and uploads both reports and HTML as run artifacts.
The local report covers current Module 4 source, including compatibility modules;
it does not claim coverage of the historical root source tree.

Lightweight TDD record
------------------------

The required contract tests were created before the new factory was implemented;
the first collection failed because ``src.flask_app`` did not exist. Once the
factory and pipeline were connected, 35 core tests passed with 69 percent combined
coverage. Parser/cleaner/configuration and error-path tests then raised statement
and branch coverage to 100 percent. Cohort-specific regression checks were added
for CS/MIT substring false positives and acceptance-rate denominators.
