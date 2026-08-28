import tkinter as tk
from tkinter import messagebox

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database
from tracker import process

current_product_id = None
products_cache = []  # listbox index -> product dict, kept in sync with the DB


def compute_moving_average(prices, window=3):
    result = []
    for i in range(len(prices)):
        start = max(0, i - window + 1)
        chunk = prices[start : i + 1]
        result.append(sum(chunk) / len(chunk))
    return result


def refresh_product_list():
    global products_cache
    products_cache = database.get_all_products()
    product_listbox.delete(0, tk.END)
    for product in products_cache:
        product_listbox.insert(tk.END, product["title"])


def select_product_in_listbox(product_id):
    for index, product in enumerate(products_cache):
        if product["_id"] == product_id:
            product_listbox.selection_clear(0, tk.END)
            product_listbox.selection_set(index)
            product_listbox.see(index)
            break


def show_product(product_id, title):
    global current_product_id
    current_product_id = product_id
    title_label.config(text=title)
    plot_graph(product_id)


def add_and_check():
    url = url_entry.get().strip()
    if not url:
        status_label.config(text="Please paste an Amazon product URL.")
        return

    title, price, message = process(url)
    if title:
        status_label.config(text=f"{title[:60]} — ₹{price} | {message}")
        url_entry.delete(0, tk.END)
        refresh_product_list()

        product = database.get_db().products.find_one({"url": url})
        if product:
            select_product_in_listbox(product["_id"])
            show_product(product["_id"], product["title"])
    else:
        status_label.config(text=message)


def check_all():
    if not products_cache:
        status_label.config(text="Watchlist is empty — add a product first.")
        return

    status_label.config(text="Checking all products...")
    window.update_idletasks()

    for product in products_cache:
        title, price, message = process(product["url"])
        print(f"{title or product['title']}: {message}")

    status_label.config(text=f"Checked {len(products_cache)} product(s). See console for details.")
    refresh_product_list()
    if current_product_id:
        plot_graph(current_product_id)


def on_select(event):
    selection = product_listbox.curselection()
    if not selection:
        return
    product = products_cache[selection[0]]
    show_product(product["_id"], product["title"])


def delete_selected():
    global current_product_id
    selection = product_listbox.curselection()
    if not selection:
        return
    product = products_cache[selection[0]]
    confirmed = messagebox.askyesno("Remove product", f"Stop tracking:\n{product['title']}?")
    if not confirmed:
        return

    database.delete_product(product["_id"])
    if current_product_id == product["_id"]:
        current_product_id = None
        title_label.config(text="Product Name")
        stats_label.config(text="")
        fig.clear()
        canvas.draw()
    refresh_product_list()


def update_stats(product_id):
    stats = database.get_price_stats(product_id)
    if not stats:
        stats_label.config(text="")
        return

    change = stats["percent_change_from_first"]
    arrow = "▼" if change < 0 else ("▲" if change > 0 else "→")
    window_size = min(stats["checks"], 5)

    stats_label.config(
        text=(
            f"Lowest: ₹{stats['lowest']:.0f}   "
            f"Highest: ₹{stats['highest']:.0f}   "
            f"Moving avg (last {window_size}): ₹{stats['moving_average']:.0f}   "
            f"Since first check: {arrow} {abs(change):.1f}%"
        )
    )


def plot_graph(product_id):
    history = database.get_price_history(product_id)
    if not history:
        stats_label.config(text="")
        return

    times = [h["timestamp"] for h in history]
    prices = [h["price"] for h in history]
    moving_avg = compute_moving_average(prices)

    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(times, prices, marker="o", label="Price")
    if len(prices) > 1:
        ax.plot(times, moving_avg, linestyle="--", label="Moving avg")
        ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_title("Price History")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (₹)")
    fig.tight_layout()
    canvas.draw()

    update_stats(product_id)


database.ensure_indexes()

# GUI
window = tk.Tk()
window.title("Amazon Price Tracker")
window.geometry("900x580")

# --- Top: add product ---
top_frame = tk.Frame(window)
top_frame.pack(fill="x", padx=10, pady=10)

tk.Label(top_frame, text="Amazon URL:").pack(side="left")
url_entry = tk.Entry(top_frame, width=60)
url_entry.pack(side="left", padx=5)
tk.Button(top_frame, text="Add & Check", command=add_and_check).pack(side="left", padx=5)
tk.Button(top_frame, text="Check All", command=check_all).pack(side="left", padx=5)

status_label = tk.Label(window, text="", wraplength=850, anchor="w", justify="left")
status_label.pack(fill="x", padx=10)

# --- Middle: watchlist + chart ---
middle_frame = tk.Frame(window)
middle_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = tk.Frame(middle_frame)
left_frame.pack(side="left", fill="y")

tk.Label(left_frame, text="Watchlist").pack()
product_listbox = tk.Listbox(left_frame, width=35, height=20)
product_listbox.pack(side="top", fill="y")
product_listbox.bind("<<ListboxSelect>>", on_select)

tk.Button(left_frame, text="Remove Selected", command=delete_selected).pack(pady=5, fill="x")

right_frame = tk.Frame(middle_frame)
right_frame.pack(side="left", fill="both", expand=True, padx=10)

title_label = tk.Label(right_frame, text="Product Name", wraplength=550)
title_label.pack()

stats_label = tk.Label(right_frame, text="", wraplength=550, fg="#444444")
stats_label.pack(pady=(2, 0))

fig = plt.Figure(figsize=(6, 3.5))
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

refresh_product_list()
window.mainloop()