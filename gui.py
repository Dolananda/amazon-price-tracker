import tkinter as tk
from tkinter import messagebox

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database
from tracker import process

current_product_id = None
products_cache = []  # listbox index -> product dict, kept in sync with the DB


def refresh_product_list():
    global products_cache
    products_cache = database.get_all_products()
    product_listbox.delete(0, tk.END)
    for product in products_cache:
        product_listbox.insert(tk.END, product["title"])


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
    global current_product_id
    selection = product_listbox.curselection()
    if not selection:
        return
    product = products_cache[selection[0]]
    current_product_id = product["_id"]
    title_label.config(text=product["title"])
    plot_graph(current_product_id)


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
        fig.clear()
        canvas.draw()
    refresh_product_list()


def plot_graph(product_id):
    history = database.get_price_history(product_id)
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


database.ensure_indexes()

# GUI
window = tk.Tk()
window.title("Amazon Price Tracker")
window.geometry("900x550")

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

fig = plt.Figure(figsize=(6, 3.5))
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

refresh_product_list()
window.mainloop()