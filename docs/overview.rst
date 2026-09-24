Overview & Setup
================

Application Architecture
------------------------
The Grad Cafe Application is structured into three main layers:

* **Web Layer (`app.py`)**: Flask web interface providing interactive controls, data visualizations, and status updates.
* **ETL Layer (`scrape.py`, `clean.py`, `load_data.py`)**: Responsible for web scraping data, cleaning raw JSON output, and loading structured records into the database.
* **DB Layer (`orm_queries.py`, `query_data.py`)**: Database abstraction layer utilizing PostgreSQL/SQLAlchemy to manage data persistence and analytical aggregations.

Required Environment Variables
------------------------------
Ensure the following environment variable is configured before running the database scripts or Flask application:

* ``DATABASE_URL``: Connection string for PostgreSQL (e.g., ``postgresql://user:password@localhost:5432/gradcafe``).

How to Run the Application
--------------------------
1. Install project dependencies:
   .. code-block:: bash

      pip install -r requirements.txt

2. Run the Flask web application:
   .. code-block:: bash

      python src/app.py

How to Run Tests
----------------
Run pytest across all marked test suites:
.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"