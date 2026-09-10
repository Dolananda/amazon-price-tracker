# Amazon Price Tracker

[![Tests](https://github.com/Dolananda/amazon-price-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dolananda/amazon-price-tracker/actions/workflows/tests.yml)

Track an Amazon product's price, store its history in MongoDB, and get emailed
the moment the price drops.

## Features

- Scrapes an Amazon product page for its current title and price
- Stores every price check in MongoDB (`products` + `price_history` collections)
- Emails you when the price drops below the last recorded price
- Track multiple products at once in a watchlist
- Simple Tkinter GUI with a live price-history chart, plus lowest/highest price,
  % change since you started tracking, and a moving-average trend line
- Auto-checks every product on a schedule in the background (toggle on/off in the GUI)
- Two interfaces: a Tkinter desktop app, or a Streamlit web dashboard — pick whichever you prefer
- Optional per-product target price — get a dedicated email the moment a price hits your target

## Quick start with Docker (web dashboard + MongoDB)

The fastest way to run the whole thing — no local Python or MongoDB install needed:

1. Copy `.env.example` to `.env` and fill in at least your email settings (the
   `MONGO_URI` value doesn't matter here — Compose overrides it automatically
   so the app can reach the `mongo` container).
2. Run:
   ```
   docker compose up --build
   ```
3. Open **http://localhost:8501** in your browser.

MongoDB's data persists in a Docker volume (`mongo-data`), so it survives
`docker compose down` / restarts. This setup only runs the web dashboard —
the Tkinter desktop app (`gui.py`) needs a real display, so it isn't
containerized; run it locally instead (see below).

## Manual setup (without Docker)

1. Clone the repo, then create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```
2. Install dependencies into it:
   ```
   pip install -r requirements.txt
   ```
   If you're using VS Code, run **Python: Select Interpreter** (Ctrl+Shift+P) and pick the
   interpreter inside `venv/` — otherwise Pylance will show "could not be resolved" warnings
   even though the packages are installed correctly.
3. Copy `.env.example` to `.env` and fill in your values:
   - `MONGO_URI` — e.g. `mongodb://localhost:27017` for local MongoDB, or your
     MongoDB Atlas connection string
   - `TRACKER_EMAIL` / `TRACKER_EMAIL_PASSWORD` — a Gmail address and an
     [App Password](https://support.google.com/accounts/answer/185833)
   - `TRACKER_RECEIVER_EMAIL` — where price-drop alerts get sent
   - `CHECK_INTERVAL_HOURS` — how often the background scheduler auto-checks prices (default `6`)
4. Make sure MongoDB is running (see below), then run either interface:
   ```
   python gui.py                    # desktop app (Tkinter)
   streamlit run streamlit_app.py   # web dashboard (opens in your browser)
   ```

## Running MongoDB locally (non-Docker path)

Easiest option is Docker, just for the database:

```
docker run -d --name price-tracker-mongo -p 27017:27017 mongo:7
```

Then leave `MONGO_URI=mongodb://localhost:27017` in `.env`. Alternatively, use
a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster and paste its
connection string into `MONGO_URI` instead.

## Data model

- `products` — one document per tracked URL: `url`, `title`, `created_at`, `last_checked`
- `price_history` — one document per price check: `product_id`, `price`, `timestamp`

## Running tests

```
pip install -r requirements-dev.txt
pytest
```

Tests run automatically on every push via GitHub Actions (see the badge at
the top). Locally: scraping and analytics tests run with no setup, but the
database tests need a MongoDB instance reachable at `MONGO_URI` — they use a
separate `amazon_price_tracker_test` database, so they never touch your real
watchlist data.