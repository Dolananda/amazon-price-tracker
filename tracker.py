import requests
from bs4 import BeautifulSoup
import smtplib
import config
import os
import csv
from datetime import datetime
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9"
}


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name[:40]


def get_data(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else "Unknown Product"

        price_tag = soup.find("span", {"class": "a-price-whole"})

        if price_tag:
            price = price_tag.get_text()
        else:
            price_tag = soup.find("span", {"class": "a-offscreen"})
            if price_tag:
                price = price_tag.get_text()
            else:
                return None, None

        price = float(price.replace("₹", "").replace(",", "").strip())

        return title, price

    except:
        return None, None


def get_csv_path(title):
    if not os.path.exists("data"):
        os.makedirs("data")

    filename = sanitize_filename(title) + ".csv"
    return os.path.join("data", filename)


def read_last_price(csv_path):
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, "r") as f:
        rows = list(csv.reader(f))
        if len(rows) > 1:
            return float(rows[-1][1])
    return None


def save_price(csv_path, price):
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Time", "Price"])

        writer.writerow([datetime.now(), price])


def send_email(title, price, url):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(config.EMAIL, config.PASSWORD)

        subject = "Price Drop Alert!"
        body = f"{title}\nNow: ₹{price}\n{url}"

        message = f"Subject: {subject}\n\n{body}"

        server.sendmail(config.EMAIL, config.RECEIVER_EMAIL, message)
        server.quit()

    except Exception as e:
        print("Email error:", e)


def process(url):
    title, price = get_data(url)

    if not price:
        return None, None, "Failed to fetch"

    csv_path = get_csv_path(title)
    last_price = read_last_price(csv_path)

    save_price(csv_path, price)

    if last_price is None:
        return title, price, "First entry saved"

    elif price < last_price:
        send_email(title, price, url)
        return title, price, f"Price dropped from ₹{last_price} → ₹{price} (Email sent)"

    else:
        return title, price, f"No drop (Last: ₹{last_price})"