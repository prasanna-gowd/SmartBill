"""
SmartBill Pro - Configuration Constants
Centralized configuration for the application.
"""

import os

# ================================================================
# Path Configuration
# ================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
BACKUPS_DIR = os.path.join(DATABASE_DIR, 'backups')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

DB_PATH = os.path.join(DATABASE_DIR, 'smartbill.db')

# ================================================================
# Application Defaults
# ================================================================

APP_NAME = "SmartBill Pro"
APP_VERSION = "2.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"

DEFAULT_TAX_RATE = 5.0
DEFAULT_NUM_TABLES = 20
DEFAULT_CURRENCY = "₹"
DEFAULT_RESTAURANT_NAME = "SmartBill Restaurant"

# ================================================================
# Window Dimensions
# ================================================================

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
MIN_WIDTH = 1200
MIN_HEIGHT = 700
SIDEBAR_WIDTH = 250
CART_PANEL_WIDTH = 380

# ================================================================
# UI Color Palette
# ================================================================

class Colors:
    """Modern design system color palette."""
    # Core
    PRIMARY = "#0f172a"
    SECONDARY = "#1e293b"
    ACCENT = "#3b82f6"
    ACCENT_HOVER = "#2563eb"

    # Surfaces
    SURFACE = "#f8fafc"
    CARD = "#ffffff"
    LIGHT_GRAY = "#f1f5f9"
    MEDIUM_GRAY = "#e2e8f0"
    BORDER = "#cbd5e1"

    # Text
    ON_SURFACE = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    WHITE = "#ffffff"

    # Semantic
    SUCCESS = "#22c55e"
    SUCCESS_DARK = "#16a34a"
    WARNING = "#f59e0b"
    WARNING_DARK = "#d97706"
    ERROR = "#ef4444"
    ERROR_DARK = "#dc2626"

    # Accent Colors
    PURPLE = "#8b5cf6"
    PURPLE_DARK = "#7c3aed"
    TEAL = "#14b8a6"

    # Sidebar
    SIDEBAR_ACTIVE = "#334155"
    SIDEBAR_HOVER = "#1e293b"


# ================================================================
# Font Configuration
# ================================================================

class Fonts:
    """Font definitions used across the application."""
    FAMILY = 'Segoe UI'
    MONO = 'Courier New'

    TITLE = (FAMILY, 28, 'bold')
    HEADING = (FAMILY, 24, 'bold')
    SUBHEADING = (FAMILY, 16, 'bold')
    BODY = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, 'bold')
    SMALL = (FAMILY, 10)
    SMALL_BOLD = (FAMILY, 10, 'bold')
    CAPTION = (FAMILY, 9)
    BUTTON = (FAMILY, 10, 'bold')
    NAV = (FAMILY, 11)
    STAT_VALUE = (FAMILY, 22, 'bold')
    RECEIPT = (MONO, 10)


# ================================================================
# Navigation Items
# ================================================================

NAV_ITEMS = [
    ('📊', 'Dashboard', 'dashboard'),
    ('🛒', 'Billing / POS', 'pos'),
    ('📋', 'Order History', 'orders'),
    ('📝', 'Menu Manager', 'menu'),
    ('📈', 'Analytics', 'analytics'),
    ('⚙️', 'Settings', 'settings'),
]

# ================================================================
# Payment Methods
# ================================================================

PAYMENT_METHODS = ['Cash', 'Card', 'UPI']

# ================================================================
# Chart Colors
# ================================================================

CHART_COLORS = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
    '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#a18cd1',
    '#fbc2eb', '#89f7fe',
]

# ================================================================
# Sample Menu Data
# ================================================================

SAMPLE_MENU_ITEMS = [
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
