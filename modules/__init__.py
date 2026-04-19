"""
SmartBill Pro - Modules Package
Provides database management, input validation, reporting, and backup utilities.
"""

from .db_manager import DatabaseManager
from .config import Colors, Fonts

__all__ = [
    'DatabaseManager',
    'Colors',
    'Fonts',
]

__version__ = '2.0'
