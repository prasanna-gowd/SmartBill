import sqlite3
import matplotlib.pyplot as plt

# Connect to DB
conn = sqlite3.connect("database/smartbill.db")
cursor = conn.cursor()

# Fetch total quantity sold per item
cursor.execute("""
    SELECT item_name, SUM(quantity) as total_qty
    FROM OrderItems
    GROUP BY item_name
    ORDER BY total_qty DESC
    LIMIT 5
""")

top_items = cursor.fetchall()

# Separate names and values
item_names = [row[0] for row in top_items]
quantities = [row[1] for row in top_items]

# Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(item_names, quantities, color="#4caf50")
plt.title("Top 5 Selling Items", fontsize=16)
plt.xlabel("Item Name", fontsize=12)
plt.ylabel("Total Quantity Sold", fontsize=12)
plt.xticks(rotation=30)

# Add data labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', fontsize=10)

plt.tight_layout()
plt.show()

conn.close()
