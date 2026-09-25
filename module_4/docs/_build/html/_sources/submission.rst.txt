Submission and verification
===========================

Repository
----------

SSH URL: ``git@github.com:Wanyiava/jhu_software_concepts.git``

The current implementation lives under ``module_4``. The original repository
source and the supplied ``module_4.1`` work remain preserved. No earlier-module
coverage result or CI screenshot is presented as proof for this revision.

Deliverables
------------

* ``module_4/src/``: Flask, ETL, schema, query modules, template, and stylesheet.
* ``module_4/tests/``: all five required test files plus data-module tests.
* ``module_4/pytest.ini``: registered markers and 100 percent coverage gate.
* ``module_4/requirements.txt`` and ``module_4/README.md``.
* ``module_4/coverage_summary.txt``: actual terminal output from the full suite.
* ``module_4/docs/`` and ``module_4/docs/_build/html/``: Sphinx sources and HTML.
* Repository-root ``.github/workflows/tests.yml`` and ``.readthedocs.yaml``.
* ``module_4/SUBMISSION_CHECKLIST.md``: current status of external deliverables.

Publishing the documentation
----------------------------

Import the confirmed public repository into Read the Docs, use ``main`` as the
default version, and build with the checked-in root configuration. Once the
build succeeds, open the actual published site and copy its URL into the Module 4
README. The project slug is assigned by Read the Docs; do not assume a URL before
the project is created or inspected.

The assignment text mentions both a private-repository rubric and a public
repository for Read the Docs. The confirmed repository is already public; no
visibility change is needed for this project.

Final evidence
--------------

After pushing the completed revision, open its successful Actions run and save
an unaltered screenshot as ``module_4/actions_success.png``. Include the run URL
and tested commit in the submission checklist. Commit the screenshot and confirm
that any follow-up workflow also succeeds. Submit the same repository revision,
SSH URL, and verified documentation link to Canvas.

Reference configuration guidance
--------------------------------

* `GitHub: PostgreSQL service containers <https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers>`_
* `Read the Docs: configuration version 2 <https://docs.readthedocs.com/platform/stable/config-file/v2.html>`_
* `SQLAlchemy: PostgreSQL INSERT ON CONFLICT <https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#insert-on-conflict-upsert>`_
