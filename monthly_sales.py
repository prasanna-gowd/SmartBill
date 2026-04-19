import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Connect to DB
conn = sqlite3.connect("database/smartbill.db")
cursor = conn.cursor()

# Fetch total sales grouped by month
cursor.execute("""
    SELECT 
        strftime('%Y-%m', datetime) as month,
        SUM(total_amount)
    FROM Orders
    GROUP BY month
    ORDER BY month
""")
data = cursor.fetchall()
conn.close()

# Split data
months = [row[0] for row in data]
totals = [row[1] for row in data]

# Plot
plt.figure(figsize=(12, 6))
bars = plt.bar(months, totals, color="#ff9800")
plt.title("📆 Monthly Sales Summary", fontsize=16)
plt.xlabel("Month (YYYY-MM)", fontsize=12)
plt.ylabel("Total Sales (₹)", fontsize=12)
plt.xticks(rotation=45)

# Add labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 10, int(yval), ha='center', fontsize=10)

plt.tight_layout()
plt.show()
