Operational notes
=================

Busy and cache policy
-----------------------

The course application runs in one process with concurrent request threads.
``ServiceState.lock`` is per-app and acquired non-blockingly by both mutation
routes. Contention returns ``409 {"busy": true}`` without scraping, loading,
querying, or changing cached results. Every exit path releases the lock.

Pulls run synchronously and return 200 only after the full database transaction
commits. The default pull is one page, bounded to at most ten pages, with a
15-second timeout per HTTP request. The browser reports progress and prevents
duplicate local clicks; server-side gating also protects other clients.

An existing analysis snapshot remains available during a pull. If no snapshot
exists yet, a busy first page request returns 409. A successful pull leaves the
snapshot unchanged until Update Analysis refreshes it. Failed refreshes retain
the last complete snapshot.

This in-process lock/cache is not a distributed job coordinator. Use a shared
queue and database/distributed locking before deploying multiple worker
processes. The development Flask server is intended for local coursework.

Uniqueness and failure atomicity
-----------------------------------

Canonical result URL is the logical identity. Scheme/host case, trailing slash,
and URL fragments are normalized; query strings are retained. The first stored
record wins on a duplicate URL. Updated content at the same URL is deliberately
not overwritten. Counts reflect inserted records, not rows scraped.

Validation precedes loading. All inserts share one transaction, so a database
constraint error rolls back earlier rows in the same batch. PostgreSQL's unique
constraint handles concurrent duplicates independently of the Python busy gate.
No table is dropped or truncated by the application.

Troubleshooting
---------------

``Set DATABASE_URL`` or database unavailable
   Set the environment variable in the same terminal used to start Flask.
   Check that PostgreSQL is ready, the port matches, and ``init-db`` ran.

``Set TEST_DATABASE_URL`` or schema permission denied
   Set an explicit disposable test database URL. The test account needs CREATE
   privilege on that database. Test failures are not silently skipped.

``No module named src``
   Run the documented commands from ``module_4``. The repository-root
   ``pytest.ini`` also redirects default test discovery to this module.

Temporary-directory permission error on Windows
   Choose a writable, disposable directory within the project, for example
   ``python -m pytest --basetemp=.pytest-tmp``. Pytest clears that directory.

Coverage fails during a focused test run
   Use ``--no-cov`` for the focused command. Run the complete suite afterward;
   do not weaken the committed 100 percent threshold.

Pull fails with HTTP 403, a timeout, or an invalid required field
   The source site may be unavailable or its markup may have changed. Check
   server logs, update the parser against a saved HTML fixture, and rerun tests.
   TLS verification stays enabled. Valid Module 3 exports can be imported offline.

Read the Docs build cannot find modules
   Keep ``.readthedocs.yaml`` at the repository root and set its Sphinx path to
   ``module_4/docs/conf.py`` and requirements path to ``module_4/requirements.txt``.
   Imports are side-effect free and must not need database/model credentials.

Prior CI screenshot is green but current code has not run
   A previous run is not evidence for a new commit. Push the completed code,
   verify that the new workflow succeeds, and capture that run's summary page.
