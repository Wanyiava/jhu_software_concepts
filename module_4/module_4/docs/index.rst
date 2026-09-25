Grad Café Analytics
===================

Module 4 adds automated verification and maintainable documentation to the
Module 3 admissions application. The service keeps the original sixteen
applicant columns and eleven analysis questions, with a Flask interface,
bounded ETL pipeline, and transactional PostgreSQL storage.

Start with :doc:`setup` to run the application. Use :doc:`testing` to reproduce
the coverage evidence and :doc:`api` to extend individual modules.

.. toctree::
   :maxdepth: 2
   :caption: Developer handbook

   setup
   architecture
   api
   testing
   operations
   submission

Design guarantees
-----------------

* Both mutation endpoints reject overlapping requests with HTTP 409.
* A batch either commits in full or rolls back in full.
* Repeated result URLs cannot create duplicate applicants.
* All percentages display exactly two decimal places.
* Tests use real PostgreSQL and fixed external-input doubles, with no live HTTP.
* Coverage includes every Python module under ``module_4/src`` and enforces
  100 percent statement and branch coverage, without exclusions.
