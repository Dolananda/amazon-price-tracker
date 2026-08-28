"""
MongoDB access layer for the Amazon Price Tracker.

Every function that talks to MongoDB lives here so the rest of the app
(tracker.py, gui.py) never has to know about collections or queries directly.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "amazon_price_tracker")

_client = None


def get_client():
    """Lazily create a single MongoClient for the process."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    return get_client()[DB_NAME]


def get_or_create_product(url: str, title: str):
    """Find a product by URL, or create it. Returns the product's _id."""
    db = get_db()
    products = db.products

    product = products.find_one({"url": url})
    if product:
        products.update_one(
            {"_id": product["_id"]},
            {"$set": {"title": title, "last_checked": datetime.utcnow()}},
        )
        return product["_id"]

    result = products.insert_one(
        {
            "url": url,
            "title": title,
            "created_at": datetime.utcnow(),
            "last_checked": datetime.utcnow(),
        }
    )
    return result.inserted_id


def save_price_point(product_id, price: float):
    db = get_db()
    db.price_history.insert_one(
        {
            "product_id": product_id,
            "price": price,
            "timestamp": datetime.utcnow(),
        }
    )


def get_last_price(product_id):
    db = get_db()
    doc = db.price_history.find_one(
        {"product_id": product_id}, sort=[("timestamp", -1)]
    )
    return doc["price"] if doc else None


def get_price_history(product_id):
    db = get_db()
    cursor = db.price_history.find({"product_id": product_id}).sort("timestamp", 1)
    return list(cursor)


def get_all_products():
    db = get_db()
    return list(db.products.find().sort("title", 1))


def get_price_stats(product_id):
    """Simple analytics over a product's price history: lowest/highest price
    seen, % change since the first check, and a short moving average.
    Returns None if there's no history yet."""
    history = get_price_history(product_id)
    if not history:
        return None

    prices = [h["price"] for h in history]
    first = prices[0]
    latest = prices[-1]
    window = prices[-5:]

    return {
        "latest": latest,
        "lowest": min(prices),
        "highest": max(prices),
        "first": first,
        "percent_change_from_first": ((latest - first) / first) * 100 if first else 0,
        "moving_average": sum(window) / len(window),
        "checks": len(prices),
    }


def delete_product(product_id):
    """Remove a product and all of its price history."""
    db = get_db()
    db.products.delete_one({"_id": product_id})
    db.price_history.delete_many({"product_id": product_id})


def ensure_indexes():
    """Create indexes for uniqueness and query performance. Safe to call
    multiple times — MongoDB is a no-op if the index already exists."""
    db = get_db()
    db.products.create_index("url", unique=True)
    db.price_history.create_index("product_id")