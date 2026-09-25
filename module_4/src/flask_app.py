"""Flask factory, injectable ETL dependencies, and observable busy-state policy."""
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable
import click
from flask import Flask, current_app, jsonify, render_template
from .clean import clean_data
from .load_data import load_data, read_records
from .models import init_db, make_engine
from .query_data import get_analysis_data
from .scrape import scrape_data


@dataclass
class ServiceState:
    """Dependencies and cache owned by one app, never shared between factories."""
    scraper: Callable
    cleaner: Callable
    loader: Callable
    query: Callable
    lock: object = field(default_factory=Lock)
    analysis: dict | None = None


def index():
    """GET / or /analysis: render the cached snapshot, initializing it once."""
    state = current_app.extensions["gradcafe"]
    if state.analysis is None:
        if not state.lock.acquire(blocking=False):
            return jsonify(busy=True), 409
        try:
            state.analysis = state.query()
        except Exception:
            current_app.logger.exception("Initial analysis query failed")
            return jsonify(ok=False, error="Analysis is unavailable. Check the database."), 503
        finally:
            state.lock.release()
    return render_template("analysis.html", results=state.analysis)


def pull_data():
    """POST /pull-data: scrape, clean, and load; return 409 when busy."""
    state = current_app.extensions["gradcafe"]
    if not state.lock.acquire(blocking=False):
        return jsonify(busy=True), 409
    try:
        inserted = state.loader(state.cleaner(state.scraper()))
        return jsonify(ok=True, inserted=inserted), 200
    except Exception:
        current_app.logger.exception("Data pull failed")
        return jsonify(ok=False, error="Data pull failed; no partial batch was saved."), 500
    finally:
        state.lock.release()


def update_analysis():
    """POST /update-analysis: refresh the snapshot or return 409 while busy."""
    state = current_app.extensions["gradcafe"]
    if not state.lock.acquire(blocking=False):
        return jsonify(busy=True), 409
    try:
        state.analysis = state.query()
        return jsonify(ok=True, results=state.analysis), 200
    except Exception:
        current_app.logger.exception("Analysis refresh failed")
        return jsonify(ok=False, error="Analysis refresh failed; the previous results are retained."), 500
    finally:
        state.lock.release()


def create_app(test_config=None, *, engine=None, scraper=None, cleaner=None,
               loader=None, query=None):
    """Create an app with optional configuration and dependency overrides.

    DATABASE_URL comes from configuration or the environment. Injected loader
    and query functions allow web tests without opening a database. Production
    and database-test requests execute the same ETL code.
    """
    app = Flask(__name__)
    app.config.from_mapping(DATABASE_URL=None, SCRAPE_PAGES=1)
    if test_config is not None:
        app.config.update(test_config)
    database = engine
    if database is None and (loader is None or query is None):
        database = make_engine(app.config["DATABASE_URL"])
    app.extensions["database"] = database
    app.extensions["gradcafe"] = ServiceState(
        scraper=scraper if scraper is not None else lambda: scrape_data(app.config["SCRAPE_PAGES"]),
        cleaner=cleaner if cleaner is not None else clean_data,
        loader=loader if loader is not None else lambda rows: load_data(rows, database),
        query=query if query is not None else lambda: get_analysis_data(database),
    )
    app.add_url_rule("/", "index", index)
    app.add_url_rule("/analysis", "analysis", index)
    app.add_url_rule("/pull-data", view_func=pull_data, methods=["POST"])
    app.add_url_rule("/update-analysis", view_func=update_analysis, methods=["POST"])

    @app.cli.command("init-db")
    def initialize_database():
        """Create the applicant table in the configured database."""
        init_db(database)
        click.echo("Database initialized.")

    @app.cli.command("import-data")
    @click.argument("filename", type=click.Path(exists=True, dir_okay=False))
    def import_data(filename):
        """Clean and transactionally import a Module 3 JSON/JSONL file."""
        count = load_data(clean_data(read_records(filename)), database)
        click.echo(f"Inserted {count} new applicants.")

    return app
