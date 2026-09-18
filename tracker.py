import logging
import re
import time

import requests
from bs4 import BeautifulSoup

import database
import notifications

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name[:40]


def get_data(url):
    """Fetch a product's title and price, retrying transient failures
    (network errors, or Amazon momentarily not returning a price) with a
    short backoff before giving up."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            title_tag = soup.find("span", {"id": "productTitle"})
            title = title_tag.get_text().strip() if title_tag else "Unknown Product"

            price_tag = soup.find("span", {"class": "a-price-whole"})
            if not price_tag:
                price_tag = soup.find("span", {"class": "a-offscreen"})
            if not price_tag:
                logger.warning("No price found (attempt %s/%s) for %s", attempt, MAX_RETRIES, url)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * attempt)
                    continue
                return None, None

            price_text = price_tag.get_text()
            price = float(price_text.replace("₹", "").replace(",", "").strip())
            return title, price
        except Exception as exc:
            logger.warning("Scrape error (attempt %s/%s) for %s: %s", attempt, MAX_RETRIES, url, exc)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)

    return None, None


def process(url):
    title, price = get_data(url)
    if not price:
        logger.error("Giving up on %s after %s attempts", url, MAX_RETRIES)
        return None, None, "Failed to fetch"

    product_id = database.get_or_create_product(url, title)
    last_price = database.get_last_price(product_id)
    database.save_price_point(product_id, price)

    product = database.get_product(product_id)
    target_price = product.get("target_price")
    target_alert_sent = product.get("target_alert_sent", False)

    if target_price is not None:
        if price <= target_price and not target_alert_sent:
            notifications.notify(
                "🎯 Target Price Reached!",
                f"{title}\nNow: ₹{price} (target was ₹{target_price})\n{url}",
            )
            database.mark_target_alert_sent(product_id, True)
        elif price > target_price and target_alert_sent:
            # Price bounced back above target — allow a future dip to alert again.
            database.mark_target_alert_sent(product_id, False)

    if last_price is None:
        message = "First entry saved"
    elif price < last_price:
        notifications.notify("Price Drop Alert!", f"{title}\nNow: ₹{price}\n{url}")
        message = f"Price dropped from ₹{last_price} → ₹{price} (Alert sent)"
    else:
        message = f"No drop (Last: ₹{last_price})"

    if target_price is not None:
        reached = "✅ reached" if price <= target_price else "not yet"
        message += f" | Target ₹{target_price}: {reached}"

    logger.info("%s: %s", title, message)
    return title, price, message
