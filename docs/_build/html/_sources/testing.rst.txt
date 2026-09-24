Testing Guide
=============

Running Marked Tests
--------------------
Tests in this project are organized using ``pytest`` custom markers. You can run individual test categories or combined marker suites:

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

   pytest -m db

   pytest -m web

Expected Selectors & Test Targets
---------------------------------
Web tests target specific Flask application endpoints and HTTP methods:

* ``/`` (GET): Main dashboard route.
* ``/pull-data`` (POST): Triggers background scraping worker process.
* ``/update-analysis`` (POST): Recalculates analytical metrics and updates DB view.

Test Doubles and Fixtures
-------------------------
To protect against live side effects (external HTTP traffic, persistent DB writes, process blocking), the test suite relies on isolated test doubles and custom helpers:

* **``unittest.mock.patch``**: Mocks out ``psycopg.connect``, ``urllib.request.urlopen``, ``subprocess.Popen``, and file I/O operations (``builtins.open``).
* **``safe_run_module``**: Custom execution isolation helper utilizing ``runpy.run_module`` to execute top-level module scripts safely without leaving lingering imports in ``sys.modules``.