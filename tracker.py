import os
import re
import smtplib

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import database

load_dotenv()

EMAIL = os.getenv("TRACKER_EMAIL")
EMAIL_PASSWORD = os.getenv("TRACKER_EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("TRACKER_RECEIVER_EMAIL", EMAIL)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name[:40]


def get_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else "Unknown Product"

        price_tag = soup.find("span", {"class": "a-price-whole"})
        if not price_tag:
            price_tag = soup.find("span", {"class": "a-offscreen"})
        if not price_tag:
            return None, None

        price_text = price_tag.get_text()
        price = float(price_text.replace("₹", "").replace(",", "").strip())
        return title, price
    except Exception as exc:
        print("Scrape error:", exc)
        return None, None


def send_email(title, price, url):
    if not EMAIL or not EMAIL_PASSWORD:
        print("Email not configured (see .env) — skipping notification.")
        return
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        subject = "Price Drop Alert!"
        body = f"{title}\nNow: ₹{price}\n{url}"
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL, RECEIVER_EMAIL, message)
        server.quit()
    except Exception as exc:
        print("Email error:", exc)


def process(url):
    title, price = get_data(url)
    if not price:
        return None, None, "Failed to fetch"

    product_id = database.get_or_create_product(url, title)
    last_price = database.get_last_price(product_id)
    database.save_price_point(product_id, price)

    if last_price is None:
        return title, price, "First entry saved"
    elif price < last_price:
        send_email(title, price, url)
        return title, price, f"Price dropped from ₹{last_price} → ₹{price} (Email sent)"
    else:
        return title, price, f"No drop (Last: ₹{last_price})"