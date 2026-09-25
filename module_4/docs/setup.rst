Overview and setup
==================

Prerequisites
-------------

Use Python 3.12 or 3.13 and PostgreSQL 16. Docker is convenient for a disposable
local database; an existing PostgreSQL installation also works. Run the commands
below from the repository's ``module_4`` directory.

.. code-block:: console

   python -m venv .venv

Activate the environment before installing: ``.venv\Scripts\Activate.ps1`` on
PowerShell, or ``source .venv/bin/activate`` on macOS/Linux.

.. code-block:: console

   python -m pip install -r requirements.txt

PostgreSQL
----------

For a disposable local instance, this command binds only to localhost. Trust
authentication is limited to this development container; use authenticated
connections for any shared or deployed database.

.. code-block:: console

   docker run --name gradcafe-dev -d -p 127.0.0.1:55432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_DB=gradcafe postgres:16-alpine

PowerShell:

.. code-block:: powershell

   $env:DATABASE_URL = "postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe"
   $env:TEST_DATABASE_URL = $env:DATABASE_URL

macOS/Linux:

.. code-block:: bash

   export DATABASE_URL='postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe'
   export TEST_DATABASE_URL="$DATABASE_URL"

.. list-table:: Configuration
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Meaning
   * - ``DATABASE_URL``
     - Required by the normal application. No fallback credentials are stored.
   * - ``TEST_DATABASE_URL``
     - Explicit disposable database for tests; requires CREATE SCHEMA permission.
   * - ``SCRAPE_PAGES``
     - Flask factory configuration key, default 1, allowed range 1–10.

Run and import
--------------

.. code-block:: console

   python -m flask --app src.flask_app:create_app init-db
   python -m flask --app src.flask_app:create_app run --port 8080

Open http://127.0.0.1:8080/analysis. Select **Pull Data** to fetch and save a bounded
batch, then **Update Analysis** to refresh the displayed snapshot. A status line
reports errors or the number of new records without navigating to a JSON page.

To import a Module 3 JSON array or multi-record JSONL export:

.. code-block:: console

   python -m flask --app src.flask_app:create_app import-data path/to/applicants.json

The cleaner accepts legacy capitalized keys and hyphenated LLM fields. Existing
enrichment is preserved; missing enrichment stays NULL. An optional ``enrich``
callable supports a separately managed LLM service without coupling tests to
model downloads. The original LLM host remains in the prior source tree.

Do not point this application at an unmigrated historical table. ``init-db``
creates missing tables but does not modify existing constraints. For existing
Module 3 data, create a fresh database, initialize it, and import the export.
This preserves the old database while enforcing URL uniqueness and core fields.

Build documentation
-------------------

.. code-block:: console

   python -m sphinx -W --keep-going -b html docs docs/_build/html

Open ``docs/_build/html/index.html``. The repository-root
``.readthedocs.yaml`` points to this configuration and installs the pinned
requirements. No database URL or live connection is needed to build the docs.
