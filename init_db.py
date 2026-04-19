import sqlite3

# Connect to SQLite (creates the DB if it doesn't exist)
conn = sqlite3.connect('database/smartbill.db')
cursor = conn.cursor()

# Create Menu table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Menu (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
)
''')

# Create Orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL,
    total_amount REAL NOT NULL
)
''')

# Create OrderItems table
cursor.execute('''
CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    item_name TEXT,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
)
''')

# Save and close
conn.commit()
conn.close()

print("✅ Database initialized.")
