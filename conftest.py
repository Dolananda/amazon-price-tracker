"""
Root-level conftest.py.

Two jobs:
1. Point the app at a separate test database *before* database.py is
   imported anywhere, so running the test suite never touches real
   watchlist data.
2. Having a conftest.py here (not inside tests/) makes pytest add the repo
   root to sys.path, so `import database`, `import tracker`, etc. work
   whether you run `pytest` or `python -m pytest`.
"""

import os

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ["MONGO_DB_NAME"] = "amazon_price_tracker_test"

import pytest

import database


@pytest.fixture
def clean_database():
    """Wipe the test database before and after a test. Only tests that
    actually need MongoDB should request this fixture — plain logic tests
    (analytics, scraping) never touch it and run fine without Mongo running."""
    db = database.get_db()
    db.products.delete_many({})
    db.price_history.delete_many({})
    yield
    db.products.delete_many({})
    db.price_history.delete_many({})
