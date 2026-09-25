Architecture
============

Request and data flow
---------------------

.. code-block:: text

   Flask client
     POST /pull-data
       -> acquire app lock
       -> scrape_data (bounded HTTP)
       -> clean_data (normalize + validate complete batch)
       -> load_data (one PostgreSQL transaction; URL uniqueness)
       -> release lock
     POST /update-analysis
       -> acquire app lock -> SQL analysis snapshot -> replace cache -> release
     GET /analysis
       -> render cached results, initializing once if necessary

Layers and responsibilities
---------------------------

* **Web:** ``flask_app.py`` owns the app factory, routes, CLI commands, cache,
  and in-process lock. ``app.py`` preserves the older factory import path.
  Templates escape values and format every percentage with ``%.2f``.
* **ETL:** ``scrape.py`` parses the supplied HTML, bounds pagination, verifies
  TLS, and applies timeouts. ``clean.py`` converts dates/numbers, maps legacy
  field names, validates identity, and preserves optional enrichment.
* **Database:** ``models.py`` defines the original schema without import-time
  connections. ``load_data.py`` uses PostgreSQL ``ON CONFLICT DO NOTHING`` for
  canonical URL duplicates and rolls back a failed batch.
* **Analysis:** ``query_data.py`` computes aggregates in PostgreSQL. The main
  aggregation and GPA-by-degree query share a repeatable-read snapshot.
  ``orm_queries.py`` delegates to this common SQLAlchemy implementation so
  separate raw/ORM versions cannot silently drift apart.

Schema and compatibility
------------------------

``applicants`` retains the sixteen original column names and types:

.. list-table:: Applicant columns
   :header-rows: 1
   :widths: 35 20 45

   * - Column(s)
     - Type
     - Policy
   * - ``p_id``
     - Integer
     - Generated primary key.
   * - ``program``, ``university``, ``status``
     - Text
     - Required, non-null core fields.
   * - ``date_added``
     - Date
     - Required, parsed before insertion.
   * - ``url``
     - Text
     - Required, unique canonical source URL.
   * - ``comments``, ``term``, ``us_or_international``, ``degree``
     - Text
     - Nullable when not reported.
   * - ``gpa``, ``gre``, ``gre_v``, ``gre_aw``
     - Float
     - Nullable; ``gre`` retains the original quantitative-score meaning.
   * - ``llm_generated_program``, ``llm_generated_university``
     - Text
     - Supplied enrichment only; nullable.

The fixture checks names, values, nullability, and the actual PostgreSQL unique
constraint. Empty optional scores are not changed to zero. Source URLs retain
their query string, so two query-based result IDs remain distinct.

Analysis contract
-----------------

The query returns ``q1`` through ``q11`` plus ``diff``. ``q3`` is a dictionary of
four average scores; ``q10`` maps degree names to average GPA. Remaining values
are numbers, except missing averages which are ``None`` and render as ``N/A``.

* Q1: Fall 2026 applicant count.
* Q2: International share among entries with known citizenship.
* Q3: Average reported GPA, GRE quantitative, verbal, and analytical writing.
* Q4: American applicants' average GPA, Fall 2026.
* Q5: Accepted share among all Fall 2025 records.
* Q6: Accepted applicants' average GPA, Fall 2026.
* Q7: Johns Hopkins CS master's applicant count.
* Q8/Q9: Fall 2026 CS PhD acceptances at Georgetown, MIT, Stanford, or CMU,
  using original/enriched names respectively; ``diff`` is Q9 minus Q8.
* Q10: Average reported GPA by degree.
* Q11: International applicants' acceptance rate, Spring 2027.

Word boundaries prevent ``Physics`` matching ``CS`` or ``Smith`` matching ``MIT``.
An acceptance starts with ``Accepted``; ``Not accepted`` is excluded.
