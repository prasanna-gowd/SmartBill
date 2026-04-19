"""
SmartBill Pro - Database Manager
Handles all database operations for the application.
"""

import sqlite3
import os
import csv
from datetime import datetime

# Resolve path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "smartbill.db")


class DatabaseManager:
    """Manages all database operations for SmartBill Pro."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self._ensure_directory()
        self.setup_database()

    def _ensure_directory(self):
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _connect(self):
        """Create a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self):
        """Create database tables and seed initial data."""
        conn = self._connect()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'staff',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Menu table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER,
                datetime TEXT NOT NULL,
                subtotal REAL NOT NULL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                tax_percent REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                status TEXT DEFAULT 'Completed',
                created_by TEXT
            )
        ''')

        # OrderItems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS OrderItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES Orders(id)
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        # ---- Schema migration for older databases ----
        migration_columns = [
            ("Orders", "subtotal", "REAL DEFAULT 0"),
            ("Orders", "discount_percent", "REAL DEFAULT 0"),
            ("Orders", "discount_amount", "REAL DEFAULT 0"),
            ("Orders", "tax_percent", "REAL DEFAULT 0"),
            ("Orders", "tax_amount", "REAL DEFAULT 0"),
            ("Orders", "payment_method", "TEXT DEFAULT 'Cash'"),
            ("Orders", "status", "TEXT DEFAULT 'Completed'"),
            ("Orders", "created_by", "TEXT"),
            ("Orders", "table_number", "INTEGER"),
            ("Menu", "is_active", "INTEGER DEFAULT 1"),
            ("OrderItems", "unit_price", "REAL DEFAULT 0"),
            ("OrderItems", "total_price", "REAL DEFAULT 0"),
        ]
        for table, col, col_type in migration_columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass  # Column already exists

        # ---- Seed default data ----

        # Default users
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
                           ("admin", "admin123", "admin"))
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
                           ("staff", "staff123", "staff"))

        # Default settings
        defaults = [
            ("restaurant_name", "SmartBill Restaurant"),
            ("tax_rate", "5"),
            ("num_tables", "20"),
            ("currency_symbol", "₹"),
        ]
        for key, value in defaults:
            cursor.execute("INSERT OR IGNORE INTO Settings (key, value) VALUES (?, ?)", (key, value))

        # Sample menu items
        cursor.execute("SELECT COUNT(*) FROM Menu WHERE is_active=1")
        if cursor.fetchone()[0] == 0:
            sample_items = [
                ("Tomato Soup", 120, "Soups"),
                ("Chicken Soup", 150, "Soups"),
                ("Sweet Corn Soup", 100, "Soups"),
                ("Manchow Soup", 130, "Soups"),
                ("Paneer Tikka", 220, "Veg Starters"),
                ("Paneer 65", 200, "Veg Starters"),
                ("Gobi Manchurian", 180, "Veg Starters"),
                ("Veg Spring Rolls", 150, "Veg Starters"),
                ("Chicken 65", 280, "Non-Veg Starters"),
                ("Chicken Lollipop", 300, "Non-Veg Starters"),
                ("Fish Fingers", 320, "Non-Veg Starters"),
                ("Prawns Fry", 350, "Non-Veg Starters"),
                ("Veg Fried Rice", 180, "Rice Items"),
                ("Egg Fried Rice", 200, "Rice Items"),
                ("Chicken Fried Rice", 220, "Rice Items"),
                ("Jeera Rice", 120, "Rice Items"),
                ("Veg Biryani", 200, "Veg Biryanis"),
                ("Paneer Biryani", 250, "Veg Biryanis"),
                ("Chicken Biryani", 320, "Non-Veg Biryanis"),
                ("Mutton Biryani", 400, "Non-Veg Biryanis"),
                ("Egg Biryani", 250, "Non-Veg Biryanis"),
                ("Family Chicken Biryani", 650, "Family Pack Biryanis"),
                ("Family Mutton Biryani", 850, "Family Pack Biryanis"),
                ("Paneer Butter Masala", 250, "Veg Curries"),
                ("Dal Tadka", 180, "Veg Curries"),
                ("Palak Paneer", 230, "Veg Curries"),
                ("Aloo Gobi", 160, "Veg Curries"),
                ("Butter Chicken", 350, "Non-Veg Curries"),
                ("Chicken Curry", 300, "Non-Veg Curries"),
                ("Mutton Curry", 420, "Non-Veg Curries"),
                ("Fish Curry", 380, "Non-Veg Curries"),
                ("Roti", 25, "Rotis"),
                ("Butter Naan", 40, "Rotis"),
                ("Garlic Naan", 50, "Rotis"),
                ("Tandoori Roti", 30, "Rotis"),
                ("French Fries", 120, "Fast Foods"),
                ("Chicken Burger", 150, "Fast Foods"),
                ("Veg Burger", 100, "Fast Foods"),
                ("Pizza (Veg)", 250, "Fast Foods"),
                ("Lassi", 80, "Beverages"),
                ("Tea", 30, "Beverages"),
                ("Coffee", 50, "Beverages"),
                ("Fresh Lime Soda", 60, "Beverages"),
                ("Coke", 40, "Beverages"),
            ]
            cursor.executemany(
                "INSERT INTO Menu (name, price, category) VALUES (?, ?, ?)", sample_items
            )

        conn.commit()
        conn.close()

    # ================================================================
    # Authentication
    # ================================================================

    def authenticate(self, username, password):
        """Authenticate a user and return their info or None."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role FROM Users WHERE username=? AND password=?",
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    # ================================================================
    # Settings
    # ================================================================

    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM Settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    def set_setting(self, key, value):
        """Set a setting value."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO Settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

    # ================================================================
    # Menu Operations
    # ================================================================

    def get_categories(self):
        """Get all active menu categories."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM Menu WHERE is_active=1 ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def get_menu_items(self, category=None, search=None):
        """Get menu items, optionally filtered by category or search term."""
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM Menu WHERE is_active=1"
        params = []

        if category:
            query += " AND category=?"
            params.append(category)
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY category, name"
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def add_menu_item(self, name, price, category):
        """Add a new menu item."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Menu (name, price, category) VALUES (?, ?, ?)",
                       (name, price, category))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id

    def update_menu_item(self, item_id, name, price, category):
        """Update an existing menu item."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE Menu SET name=?, price=?, category=? WHERE id=?",
                       (name, price, category, item_id))
        conn.commit()
        conn.close()

    def delete_menu_item(self, item_id):
        """Soft-delete a menu item."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE Menu SET is_active=0 WHERE id=?", (item_id,))
        conn.commit()
        conn.close()

    # ================================================================
    # Order Operations
    # ================================================================

    def place_order(self, table_number, items, subtotal, discount_pct, discount_amt,
                    tax_pct, tax_amt, total, payment_method='Cash', created_by=''):
        """Place a new order and return the order ID."""
        conn = self._connect()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO Orders (table_number, datetime, subtotal, discount_percent,
            discount_amount, tax_percent, tax_amount, total_amount, payment_method, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (table_number, now, subtotal, discount_pct, discount_amt,
              tax_pct, tax_amt, total, payment_method, created_by))

        order_id = cursor.lastrowid

        for item in items:
            unit_price = item['price']
            total_price = item['qty'] * unit_price
            cursor.execute("""
                INSERT INTO OrderItems (order_id, item_name, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item['name'], item['qty'], unit_price, total_price))

        conn.commit()
        conn.close()
        return order_id

    def get_orders(self, start_date=None, end_date=None, table_number=None, limit=None):
        """Get orders with optional filters."""
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM Orders WHERE 1=1"
        params = []

        if start_date:
            query += " AND DATE(datetime) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(datetime) <= ?"
            params.append(end_date)
        if table_number:
            query += " AND table_number=?"
            params.append(table_number)

        query += " ORDER BY datetime DESC"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders

    def get_order_items(self, order_id):
        """Get all items for a specific order."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OrderItems WHERE order_id=?", (order_id,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    # ================================================================
    # Analytics
    # ================================================================

    def get_dashboard_stats(self):
        """Get summary statistics for the dashboard."""
        conn = self._connect()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM Orders WHERE DATE(datetime)=?",
            (today,),
        )
        today_orders, today_revenue = cursor.fetchone()

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM Orders")
        total_orders, total_revenue = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM Menu WHERE is_active=1")
        menu_count = cursor.fetchone()[0]

        avg_order = total_revenue / total_orders if total_orders > 0 else 0

        conn.close()
        return {
            'today_orders': today_orders,
            'today_revenue': round(today_revenue, 2),
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'menu_count': menu_count,
            'avg_order': round(avg_order, 2),
        }

    def get_top_items(self, limit=5, start_date=None, end_date=None):
        """Get top selling items by quantity."""
        conn = self._connect()
        cursor = conn.cursor()

        query = """
            SELECT item_name, SUM(quantity) as total_qty,
                   SUM(total_price) as total_revenue
            FROM OrderItems
        """
        params = []

        if start_date or end_date:
            query += " WHERE order_id IN (SELECT id FROM Orders WHERE 1=1"
            if start_date:
                query += " AND DATE(datetime) >= ?"
                params.append(start_date)
            if end_date:
                query += " AND DATE(datetime) <= ?"
                params.append(end_date)
            query += ")"

        query += f" GROUP BY item_name ORDER BY total_qty DESC LIMIT {limit}"
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def get_daily_sales(self, start_date, end_date):
        """Get daily sales data for a date range."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(datetime) as date, SUM(total_amount) as total,
                   COUNT(*) as order_count
            FROM Orders
            WHERE DATE(datetime) BETWEEN ? AND ?
            GROUP BY DATE(datetime)
            ORDER BY date
        """, (start_date, end_date))
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    def get_monthly_sales(self, limit=12):
        """Get monthly sales summary."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%%Y-%%m', datetime) as month,
                   SUM(total_amount) as total, COUNT(*) as order_count
            FROM Orders
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
        """, (limit,))
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    def get_category_sales(self):
        """Get sales breakdown by category."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(m.category, 'Other') as category,
                   SUM(oi.total_price) as total
            FROM OrderItems oi
            LEFT JOIN Menu m ON oi.item_name = m.name AND m.is_active = 1
            GROUP BY category
            ORDER BY total DESC
        """)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    def get_hourly_distribution(self):
        """Get order distribution by hour of day."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CAST(strftime('%%H', datetime) AS INTEGER) as hour,
                   COUNT(*) as count
            FROM Orders
            GROUP BY hour
            ORDER BY hour
        """)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    # ================================================================
    # Export
    # ================================================================

    def export_orders_csv(self, filepath, start_date=None, end_date=None):
        """Export orders to a CSV file."""
        orders = self.get_orders(start_date, end_date)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Order ID', 'Table', 'Date/Time', 'Subtotal', 'Discount %',
                'Discount Amt', 'Tax %', 'Tax Amt', 'Total', 'Payment', 'Status', 'Staff'
            ])
            for order in orders:
                writer.writerow([
                    order['id'], order.get('table_number', ''),
                    order['datetime'],
                    order.get('subtotal', order['total_amount']),
                    order.get('discount_percent', 0),
                    order.get('discount_amount', 0),
                    order.get('tax_percent', 0),
                    order.get('tax_amount', 0),
                    order['total_amount'],
                    order.get('payment_method', 'Cash'),
                    order.get('status', 'Completed'),
                    order.get('created_by', ''),
                ])

        return filepath
