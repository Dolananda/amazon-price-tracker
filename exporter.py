"""
CSV export helpers.

Kept UI-agnostic on purpose: functions here return CSV as a string so the
desktop app can write it to a file and the web dashboard can hand it straight
to a download button, without either duplicating the formatting logic.
"""

import csv
import io

import database


def price_history_to_csv(product_id):
    """Return a product's full price history as a CSV string."""
    history = database.get_price_history(product_id)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["timestamp", "price"])
    for entry in history:
        writer.writerow([entry["timestamp"].isoformat(), entry["price"]])
    return buffer.getvalue()


def watchlist_summary_to_csv():
    """Return a summary row per tracked product as a CSV string."""
    summary = database.get_watchlist_summary()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["title", "url", "latest", "lowest", "highest", "drop_from_high_pct", "target_price", "checks"]
    )
    for row in summary:
        writer.writerow(
            [
                row["title"],
                row["url"],
                row["latest"],
                row["lowest"],
                row["highest"],
                f"{row['drop_from_high_pct']:.2f}",
                row["target_price"] if row["target_price"] is not None else "",
                row["checks"],
            ]
        )
    return buffer.getvalue()
