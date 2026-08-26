import tkinter as tk

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database
from tracker import process

current_product_id = None


def run_tracker():
    global current_product_id
    url = url_entry.get().strip()
    if not url:
        result_label.config(text="Please paste an Amazon product URL.")
        return

    title, price, message = process(url)
    if title:
        title_label.config(text=title)
        result_label.config(text=f"₹{price} | {message}")
        product = database.get_db().products.find_one({"url": url})
        current_product_id = product["_id"]
        plot_graph()
    else:
        result_label.config(text=message)


def plot_graph():
    if current_product_id is None:
        return

    history = database.get_price_history(current_product_id)
    if not history:
        return

    times = [h["timestamp"] for h in history]
    prices = [h["price"] for h in history]

    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(times, prices, marker="o")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_title("Price History")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (₹)")
    fig.tight_layout()
    canvas.draw()


# GUI
window = tk.Tk()
window.title("Amazon Price Tracker")
window.geometry("700x500")

tk.Label(window, text="Amazon URL:").pack()
url_entry = tk.Entry(window, width=80)
url_entry.pack(pady=5)

tk.Button(window, text="Check Price", command=run_tracker).pack(pady=10)

title_label = tk.Label(window, text="Product Name", wraplength=600)
title_label.pack()
result_label = tk.Label(window, text="")
result_label.pack(pady=5)

# Graph area
fig = plt.Figure(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack()

window.mainloop()