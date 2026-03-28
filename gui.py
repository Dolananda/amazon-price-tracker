import tkinter as tk
from tracker import process
import pandas as pd
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


current_csv = None


def run_tracker():
    global current_csv

    url = url_entry.get()
    title, price, message = process(url)

    if title:
        title_label.config(text=title)
        result_label.config(text=f"₹{price} | {message}")

        # find csv file
        filename = title[:40].replace("/", "") + ".csv"
        current_csv = os.path.join("data", filename)

        plot_graph()


def plot_graph():
    if not current_csv or not os.path.exists(current_csv):
        return

    data = pd.read_csv(current_csv)

    data["Time"] = pd.to_datetime(data["Time"])

    data = data.sort_values("Time")

    fig.clear()
    ax = fig.add_subplot(111)

    ax.plot(data["Time"], data["Price"], marker='o')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    ax.set_title("Price History")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")

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