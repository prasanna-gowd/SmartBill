import sqlite3
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime

# ---------- DB Functions ----------

def fetch_sales_data(start_date, end_date):
    conn = sqlite3.connect("database/smartbill.db")
    cursor = conn.cursor()
    query = """
        SELECT DATE(datetime) as date, SUM(total_amount)
        FROM Orders
        WHERE DATE(datetime) BETWEEN ? AND ?
        GROUP BY DATE(datetime)
        ORDER BY date
    """
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_top_items(start_date, end_date):
    conn = sqlite3.connect("database/smartbill.db")
    cursor = conn.cursor()
    query = """
        SELECT item_name, SUM(quantity) as total_qty
        FROM OrderItems
        WHERE order_id IN (
            SELECT order_id FROM Orders WHERE DATE(datetime) BETWEEN ? AND ?
        )
        GROUP BY item_name
        ORDER BY total_qty DESC
        LIMIT 5
    """
    cursor.execute(query, (start_date, end_date))
    items = cursor.fetchall()
    conn.close()
    return items

# ---------- Plotting Functions ----------

def show_sales_chart():
    start = from_date.get_date().strftime("%Y-%m-%d")
    end = to_date.get_date().strftime("%Y-%m-%d")

    data = fetch_sales_data(start, end)
    if not data:
        messagebox.showinfo("No Data", "No sales in this date range.")
        return

    dates = [row[0] for row in data]
    totals = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(dates, totals, color="#2196f3")
    plt.title(f"Sales from {start} to {end}", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Total Sales (₹)")
    plt.xticks(rotation=45)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 10, int(yval), ha='center')
    plt.tight_layout()
    plt.show()

def show_top_items_chart():
    start = from_date.get_date().strftime("%Y-%m-%d")
    end = to_date.get_date().strftime("%Y-%m-%d")

    items = fetch_top_items(start, end)
    if not items:
        messagebox.showinfo("No Data", "No orders in this date range.")
        return

    names = [row[0] for row in items]
    qtys = [row[1] for row in items]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, qtys, color="#4caf50")
    plt.title(f"Top-Selling Items ({start} to {end})", fontsize=14)
    plt.xlabel("Item Name")
    plt.ylabel("Quantity Sold")
    plt.xticks(rotation=45)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, int(yval), ha='center')
    plt.tight_layout()
    plt.show()

# ---------- GUI Setup ----------

window = tk.Tk()
window.title("SmartBill - Sales Analysis")
window.geometry("420x300")
window.config(bg="#f0f0f0")

tk.Label(window, text="📊 Sales Analytics", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(pady=10)

frame = tk.Frame(window, bg="#f0f0f0")
frame.pack(pady=10)

tk.Label(frame, text="From:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=10)
from_date = DateEntry(frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
from_date.grid(row=0, column=1)

tk.Label(frame, text="To:", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
to_date = DateEntry(frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
to_date.grid(row=1, column=1)

btn1 = tk.Button(window, text="Show Sales", font=("Arial", 12, "bold"), bg="#2196f3", fg="white", width=20, command=show_sales_chart)
btn1.pack(pady=5)

btn2 = tk.Button(window, text="Show Top Items", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", width=20, command=show_top_items_chart)
btn2.pack(pady=5)

window.mainloop()
