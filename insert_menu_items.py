import sqlite3

items = [
    ("Veg Hot & Sour", "Soups", 80),
    ("Chicken Hot & Sour", "Soups", 100),
    ("Paneer 65", "Veg Starters", 120),
    ("Chicken Lollipop", "Non-Veg Starters", 150),
    ("Veg Fried Rice", "Rice Items", 90),
    ("Chicken Biryani", "Non-Veg Biryanis", 160),
    ("Family Chicken Biryani", "Family Pack Biryanis", 350),
    ("Paneer Butter Masala", "Veg Curries", 130),
    ("Butter Naan", "Rotis", 25),
    ("Coke", "Beverages", 40),
    ("Chicken Burger", "Fast Foods", 110)
]

conn = sqlite3.connect("database/smartbill.db")
cursor = conn.cursor()

cursor.executemany("INSERT INTO Menu (name, category, price) VALUES (?, ?, ?)", items)

conn.commit()
conn.close()
print("✅ Sample items inserted into Menu table.")
