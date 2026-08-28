# Amazon Price Tracker

Track an Amazon product's price, store its history in MongoDB, and get emailed
the moment the price drops.

## Features

- Scrapes an Amazon product page for its current title and price
- Stores every price check in MongoDB (`products` + `price_history` collections)
- Emails you when the price drops below the last recorded price
- Track multiple products at once in a watchlist
- Simple Tkinter GUI with a live price-history chart, plus lowest/highest price,
  % change since you started tracking, and a moving-average trend line

## Setup

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
4. Make sure MongoDB is running (see below), then run:
   ```
   python gui.py
   ```

## Running MongoDB locally

Easiest option is Docker:

```
docker run -d --name price-tracker-mongo -p 27017:27017 mongo:7
```

Then leave `MONGO_URI=mongodb://localhost:27017` in `.env`. Alternatively, use
a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster and paste its
connection string into `MONGO_URI` instead.

## Data model

- `products` — one document per tracked URL: `url`, `title`, `created_at`, `last_checked`
- `price_history` — one document per price check: `product_id`, `price`, `timestamp`