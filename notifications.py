"""
Notification channels for price alerts.

Each channel is independently optional — configure any combination via
.env, including none (alerts are just skipped/logged, nothing crashes).
`notify()` is the single entry point tracker.py calls; it fans out to
whichever channels are configured.
"""

import os
import smtplib

import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("TRACKER_EMAIL")
EMAIL_PASSWORD = os.getenv("TRACKER_EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("TRACKER_RECEIVER_EMAIL", EMAIL)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_email(subject, body):
    if not EMAIL or not EMAIL_PASSWORD:
        print("Email not configured (see .env) — skipping.")
        return
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL, RECEIVER_EMAIL, message)
        server.quit()
    except Exception as exc:
        print("Email error:", exc)


def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as exc:
        print("Telegram error:", exc)


def send_discord(message):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as exc:
        print("Discord error:", exc)


def notify(subject, body):
    """Send an alert through every configured channel. Channels that aren't
    configured are silently skipped — safe to call even with nothing set up."""
    send_email(subject, body)
    send_telegram(f"{subject}\n{body}")
    send_discord(f"**{subject}**\n{body}")
