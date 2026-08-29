"""
Background scheduler that periodically checks every tracked product's price,
so the watchlist stays up to date without manual "Check All" clicks.

Kept separate from gui.py on purpose: this module has no Tkinter dependency,
so it can just as easily be driven by a future web dashboard or run headless.
"""

import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

import database
from tracker import process

load_dotenv()

CHECK_INTERVAL_HOURS = float(os.getenv("CHECK_INTERVAL_HOURS", "6"))

_scheduler = None


def check_all_products():
    """Check every product currently in the watchlist. Only touches the
    database and network, so it's safe to call from a background thread."""
    products = database.get_all_products()
    for product in products:
        title, price, message = process(product["url"])
        print(f"[scheduled check] {title or product['title']}: {message}")
    return products


def start(on_complete=None):
    """Start the background scheduler if it isn't already running.

    `on_complete`, if given, is called with no arguments after each scheduled
    run finishes. It fires on APScheduler's own thread — if the caller needs
    to touch a GUI, it should hand off to the main thread itself (e.g. via
    Tkinter's `window.after(0, ...)`).
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()

    def job():
        check_all_products()
        if on_complete:
            on_complete()

    _scheduler.add_job(
        job,
        "interval",
        hours=CHECK_INTERVAL_HOURS,
        id="check_all_products",
        replace_existing=True,
    )
    _scheduler.start()
    return _scheduler


def stop():
    """Stop the background scheduler, if running."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None