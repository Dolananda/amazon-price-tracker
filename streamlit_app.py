"""
Web dashboard for the Amazon Price Tracker, built with Streamlit.

An alternative to gui.py — same MongoDB backend, same features, but runs in
a browser instead of a desktop window. Start it with:

    streamlit run streamlit_app.py
"""

import pandas as pd
import streamlit as st

import database
import scheduler
from analytics import compute_moving_average
from tracker import process

st.set_page_config(page_title="Amazon Price Tracker", page_icon="📦", layout="wide")

database.ensure_indexes()
scheduler.start()  # idempotent — safe to call on every rerun

st.title("📦 Amazon Price Tracker")

# --- Sidebar: add a product / bulk actions ---
with st.sidebar:
    st.header("Add a product")
    url = st.text_input("Amazon product URL")
    if st.button("Add & Check", use_container_width=True):
        if url.strip():
            title, price, message = process(url.strip())
            if title:
                st.success(f"{title[:60]} — ₹{price} | {message}")
            else:
                st.error(message)
        else:
            st.warning("Paste an Amazon product URL first.")

    st.divider()
    if st.button("Check all products", use_container_width=True):
        with st.spinner("Checking every product..."):
            scheduler.check_all_products()
        st.success("Done.")

    st.caption(f"Background auto-check also runs every {scheduler.CHECK_INTERVAL_HOURS:g}h.")

# --- Main: watchlist ---
products = database.get_all_products()

if not products:
    st.info("Your watchlist is empty. Add a product URL from the sidebar to get started.")
else:
    titles = [p["title"] for p in products]
    selected_title = st.selectbox("Select a product", titles)
    selected_product = next(p for p in products if p["title"] == selected_title)

    stats = database.get_price_stats(selected_product["_id"])
    history = database.get_price_history(selected_product["_id"])

    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latest", f"₹{stats['latest']:.0f}")
        col2.metric("Lowest ever", f"₹{stats['lowest']:.0f}")
        col3.metric("Highest ever", f"₹{stats['highest']:.0f}")
        col4.metric("Since first check", f"{stats['percent_change_from_first']:+.1f}%")

    if history:
        df = pd.DataFrame(history)[["timestamp", "price"]].copy()
        df["moving_avg"] = compute_moving_average(df["price"].tolist())
        st.line_chart(df.set_index("timestamp"))
    else:
        st.info("No price history yet for this product.")

    if st.button("Remove from watchlist"):
        database.delete_product(selected_product["_id"])
        st.rerun()
