"""
SmartBill Pro - Unit Tests
Tests for database manager, validators, and report generator.
"""

import unittest
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DatabaseManager
from modules.validators import (
    validate_price, validate_quantity, validate_discount,
    validate_tax_rate, validate_item_name, validate_category,
    validate_username, validate_password, validate_date,
    sanitize_string
)


class TestValidators(unittest.TestCase):
    """Tests for the input validation module."""

    # --- Price Validation ---
    def test_valid_price(self):
        valid, value, msg = validate_price("250")
        self.assertTrue(valid)
        self.assertEqual(value, 250.0)

    def test_price_with_decimals(self):
        valid, value, msg = validate_price("99.50")
        self.assertTrue(valid)
        self.assertEqual(value, 99.50)

    def test_negative_price(self):
        valid, value, msg = validate_price("-10")
        self.assertFalse(valid)
        self.assertIn("greater than zero", msg)

    def test_zero_price(self):
        valid, value, msg = validate_price("0")
        self.assertFalse(valid)

    def test_invalid_price_string(self):
        valid, value, msg = validate_price("abc")
        self.assertFalse(valid)
        self.assertIn("valid number", msg)

    def test_excessive_price(self):
        valid, value, msg = validate_price("200000")
        self.assertFalse(valid)
        self.assertIn("exceed", msg)

    # --- Quantity Validation ---
    def test_valid_quantity(self):
        valid, value, msg = validate_quantity("5")
        self.assertTrue(valid)
        self.assertEqual(value, 5)

    def test_zero_quantity(self):
        valid, value, msg = validate_quantity("0")
        self.assertFalse(valid)

    def test_negative_quantity(self):
        valid, value, msg = validate_quantity("-3")
        self.assertFalse(valid)

    def test_float_quantity(self):
        valid, value, msg = validate_quantity("2.5")
        self.assertFalse(valid)

    # --- Discount Validation ---
    def test_valid_discount(self):
        valid, value, msg = validate_discount("10")
        self.assertTrue(valid)
        self.assertEqual(value, 10.0)

    def test_zero_discount(self):
        valid, value, msg = validate_discount("0")
        self.assertTrue(valid)

    def test_max_discount(self):
        valid, value, msg = validate_discount("100")
        self.assertTrue(valid)

    def test_over_100_discount(self):
        valid, value, msg = validate_discount("150")
        self.assertFalse(valid)

    def test_negative_discount(self):
        valid, value, msg = validate_discount("-5")
        self.assertFalse(valid)

    # --- Tax Rate Validation ---
    def test_valid_tax(self):
        valid, value, msg = validate_tax_rate("5")
        self.assertTrue(valid)
        self.assertEqual(value, 5.0)

    def test_excessive_tax(self):
        valid, value, msg = validate_tax_rate("60")
        self.assertFalse(valid)

    # --- Item Name Validation ---
    def test_valid_item_name(self):
        valid, value, msg = validate_item_name("Chicken Biryani")
        self.assertTrue(valid)
        self.assertEqual(value, "Chicken Biryani")

    def test_empty_item_name(self):
        valid, value, msg = validate_item_name("")
        self.assertFalse(valid)

    def test_whitespace_item_name(self):
        valid, value, msg = validate_item_name("   ")
        self.assertFalse(valid)

    def test_short_item_name(self):
        valid, value, msg = validate_item_name("A")
        self.assertFalse(valid)

    def test_item_name_strips_whitespace(self):
        valid, value, msg = validate_item_name("  Paneer Tikka  ")
        self.assertTrue(valid)
        self.assertEqual(value, "Paneer Tikka")

    # --- Category Validation ---
    def test_valid_category(self):
        valid, value, msg = validate_category("Non-Veg Starters")
        self.assertTrue(valid)

    def test_empty_category(self):
        valid, value, msg = validate_category("")
        self.assertFalse(valid)

    # --- Username Validation ---
    def test_valid_username(self):
        valid, value, msg = validate_username("admin")
        self.assertTrue(valid)
        self.assertEqual(value, "admin")

    def test_username_with_numbers(self):
        valid, value, msg = validate_username("staff_01")
        self.assertTrue(valid)

    def test_short_username(self):
        valid, value, msg = validate_username("ab")
        self.assertFalse(valid)

    def test_username_special_chars(self):
        valid, value, msg = validate_username("user@name")
        self.assertFalse(valid)

    def test_username_uppercase_normalized(self):
        valid, value, msg = validate_username("Admin")
        self.assertTrue(valid)
        self.assertEqual(value, "admin")

    # --- Password Validation ---
    def test_valid_password(self):
        valid, value, msg = validate_password("admin123")
        self.assertTrue(valid)

    def test_short_password(self):
        valid, value, msg = validate_password("abc")
        self.assertFalse(valid)

    def test_empty_password(self):
        valid, value, msg = validate_password("")
        self.assertFalse(valid)

    # --- Date Validation ---
    def test_valid_date(self):
        valid, value, msg = validate_date("2026-04-19")
        self.assertTrue(valid)

    def test_invalid_date_format(self):
        valid, value, msg = validate_date("19-04-2026")
        self.assertFalse(valid)

    def test_invalid_date_value(self):
        valid, value, msg = validate_date("2026-13-45")
        self.assertFalse(valid)

    # --- Sanitize String ---
    def test_sanitize_normal(self):
        result = sanitize_string("  Hello World  ")
        self.assertEqual(result, "Hello World")

    def test_sanitize_none(self):
        result = sanitize_string(None)
        self.assertEqual(result, "")

    def test_sanitize_max_length(self):
        result = sanitize_string("A" * 500, max_length=10)
        self.assertEqual(len(result), 10)


class TestDatabaseManager(unittest.TestCase):
    """Tests for the DatabaseManager class."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary database for testing."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, 'test_smartbill.db')
        cls.db = DatabaseManager(db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        """Remove temporary database."""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_database_created(self):
        """Test that the database file was created."""
        self.assertTrue(os.path.exists(self.db_path))

    def test_default_users_seeded(self):
        """Test that default users were created."""
        user = self.db.authenticate('admin', 'admin123')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'admin')
        self.assertEqual(user['role'], 'admin')

    def test_staff_user_exists(self):
        """Test that the staff user exists."""
        user = self.db.authenticate('staff', 'staff123')
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'staff')

    def test_invalid_login(self):
        """Test that invalid credentials return None."""
        user = self.db.authenticate('admin', 'wrongpassword')
        self.assertIsNone(user)

    def test_nonexistent_user(self):
        """Test that nonexistent user returns None."""
        user = self.db.authenticate('nobody', 'password')
        self.assertIsNone(user)

    def test_menu_items_seeded(self):
        """Test that sample menu items were created."""
        items = self.db.get_menu_items()
        self.assertGreater(len(items), 0)

    def test_get_categories(self):
        """Test that categories are returned."""
        categories = self.db.get_categories()
        self.assertGreater(len(categories), 0)
        self.assertIn('Soups', categories)

    def test_filter_by_category(self):
        """Test menu filtering by category."""
        items = self.db.get_menu_items(category='Soups')
        self.assertGreater(len(items), 0)
        for item in items:
            self.assertEqual(item['category'], 'Soups')

    def test_search_menu(self):
        """Test menu search functionality."""
        items = self.db.get_menu_items(search='chicken')
        self.assertGreater(len(items), 0)
        for item in items:
            self.assertIn('chicken', item['name'].lower())

    def test_add_menu_item(self):
        """Test adding a new menu item."""
        item_id = self.db.add_menu_item('Test Item', 199.0, 'Test Category')
        self.assertIsNotNone(item_id)
        self.assertGreater(item_id, 0)

    def test_update_menu_item(self):
        """Test updating a menu item."""
        item_id = self.db.add_menu_item('Update Test', 100.0, 'Test')
        self.db.update_menu_item(item_id, 'Updated Item', 150.0, 'Updated Category')

        items = self.db.get_menu_items(search='Updated Item')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['price'], 150.0)

    def test_delete_menu_item(self):
        """Test soft-deleting a menu item."""
        item_id = self.db.add_menu_item('Delete Test', 50.0, 'Test')
        self.db.delete_menu_item(item_id)

        # Item should not appear in active items
        items = self.db.get_menu_items(search='Delete Test')
        self.assertEqual(len(items), 0)

    def test_settings_get_default(self):
        """Test getting a setting with default value."""
        value = self.db.get_setting('nonexistent_key', 'default_val')
        self.assertEqual(value, 'default_val')

    def test_settings_set_and_get(self):
        """Test setting and retrieving a value."""
        self.db.set_setting('test_key', 'test_value')
        value = self.db.get_setting('test_key')
        self.assertEqual(value, 'test_value')

    def test_default_settings(self):
        """Test that default settings were seeded."""
        tax = self.db.get_setting('tax_rate')
        self.assertEqual(tax, '5')

        name = self.db.get_setting('restaurant_name')
        self.assertEqual(name, 'SmartBill Restaurant')

    def test_place_order(self):
        """Test placing an order."""
        items = [
            {'name': 'Chicken Biryani', 'price': 320, 'qty': 2},
            {'name': 'Butter Naan', 'price': 40, 'qty': 4},
        ]
        order_id = self.db.place_order(
            table_number=5, items=items,
            subtotal=800, discount_pct=10, discount_amt=80,
            tax_pct=5, tax_amt=36, total=756,
            payment_method='Card', created_by='admin'
        )
        self.assertIsNotNone(order_id)
        self.assertGreater(order_id, 0)

    def test_get_orders(self):
        """Test retrieving orders."""
        orders = self.db.get_orders()
        self.assertIsInstance(orders, list)

    def test_get_order_items(self):
        """Test retrieving order items."""
        # Place an order first
        items = [{'name': 'Tea', 'price': 30, 'qty': 1}]
        order_id = self.db.place_order(
            table_number=1, items=items,
            subtotal=30, discount_pct=0, discount_amt=0,
            tax_pct=5, tax_amt=1.5, total=31.5
        )
        order_items = self.db.get_order_items(order_id)
        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0]['item_name'], 'Tea')

    def test_dashboard_stats(self):
        """Test dashboard statistics."""
        stats = self.db.get_dashboard_stats()
        self.assertIn('today_orders', stats)
        self.assertIn('total_revenue', stats)
        self.assertIn('menu_count', stats)
        self.assertIn('avg_order', stats)

    def test_top_items(self):
        """Test top items query."""
        items = self.db.get_top_items(5)
        self.assertIsInstance(items, list)

    def test_category_sales(self):
        """Test category sales query."""
        data = self.db.get_category_sales()
        self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
