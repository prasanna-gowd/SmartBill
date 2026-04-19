"""
SmartBill Pro - Input Validators
Provides validation functions for user inputs across the application.
"""

import re


def validate_price(value):
    """Validate that a price is a positive number.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: float or None, error_msg: str)
    """
    try:
        price = float(value)
        if price <= 0:
            return False, None, "Price must be greater than zero."
        if price > 100000:
            return False, None, "Price cannot exceed ₹1,00,000."
        return True, round(price, 2), ""
    except (ValueError, TypeError):
        return False, None, "Please enter a valid number."


def validate_quantity(value):
    """Validate that a quantity is a positive integer.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: int or None, error_msg: str)
    """
    try:
        qty = int(value)
        if qty <= 0:
            return False, None, "Quantity must be at least 1."
        if qty > 999:
            return False, None, "Quantity cannot exceed 999."
        return True, qty, ""
    except (ValueError, TypeError):
        return False, None, "Please enter a valid whole number."


def validate_discount(value):
    """Validate that a discount percentage is within range.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: float or None, error_msg: str)
    """
    try:
        discount = float(value)
        if discount < 0:
            return False, None, "Discount cannot be negative."
        if discount > 100:
            return False, None, "Discount cannot exceed 100%."
        return True, round(discount, 2), ""
    except (ValueError, TypeError):
        return False, None, "Please enter a valid percentage."


def validate_tax_rate(value):
    """Validate that a tax rate is within a reasonable range.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: float or None, error_msg: str)
    """
    try:
        rate = float(value)
        if rate < 0:
            return False, None, "Tax rate cannot be negative."
        if rate > 50:
            return False, None, "Tax rate cannot exceed 50%."
        return True, round(rate, 2), ""
    except (ValueError, TypeError):
        return False, None, "Please enter a valid tax rate."


def validate_table_count(value):
    """Validate the number of tables.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: int or None, error_msg: str)
    """
    try:
        count = int(value)
        if count < 1:
            return False, None, "Must have at least 1 table."
        if count > 100:
            return False, None, "Cannot exceed 100 tables."
        return True, count, ""
    except (ValueError, TypeError):
        return False, None, "Please enter a valid number."


def validate_item_name(value):
    """Validate a menu item name.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: str or None, error_msg: str)
    """
    if not value or not value.strip():
        return False, None, "Item name cannot be empty."

    name = value.strip()

    if len(name) < 2:
        return False, None, "Item name must be at least 2 characters."
    if len(name) > 100:
        return False, None, "Item name cannot exceed 100 characters."

    return True, name, ""


def validate_category(value):
    """Validate a category name.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: str or None, error_msg: str)
    """
    if not value or not value.strip():
        return False, None, "Category cannot be empty."

    category = value.strip()

    if len(category) < 2:
        return False, None, "Category must be at least 2 characters."
    if len(category) > 50:
        return False, None, "Category cannot exceed 50 characters."

    return True, category, ""


def validate_username(value):
    """Validate a username.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: str or None, error_msg: str)
    """
    if not value or not value.strip():
        return False, None, "Username cannot be empty."

    username = value.strip().lower()

    if len(username) < 3:
        return False, None, "Username must be at least 3 characters."
    if len(username) > 30:
        return False, None, "Username cannot exceed 30 characters."
    if not re.match(r'^[a-z0-9_]+$', username):
        return False, None, "Username can only contain letters, numbers, and underscores."

    return True, username, ""


def validate_password(value):
    """Validate a password.

    Args:
        value: The input to validate.

    Returns:
        tuple: (is_valid: bool, cleaned_value: str or None, error_msg: str)
    """
    if not value:
        return False, None, "Password cannot be empty."

    if len(value) < 4:
        return False, None, "Password must be at least 4 characters."
    if len(value) > 50:
        return False, None, "Password cannot exceed 50 characters."

    return True, value, ""


def validate_date(value, format_str="%Y-%m-%d"):
    """Validate a date string.

    Args:
        value: The date string to validate.
        format_str: Expected date format (default: YYYY-MM-DD).

    Returns:
        tuple: (is_valid: bool, cleaned_value: str or None, error_msg: str)
    """
    from datetime import datetime

    if not value or not value.strip():
        return False, None, "Date cannot be empty."

    try:
        parsed = datetime.strptime(value.strip(), format_str)
        return True, parsed.strftime(format_str), ""
    except ValueError:
        return False, None, f"Invalid date format. Use {format_str}."


def sanitize_string(value, max_length=200):
    """Sanitize a string input by stripping whitespace and limiting length.

    Args:
        value: The string to sanitize.
        max_length: Maximum allowed length.

    Returns:
        str: Sanitized string.
    """
    if not value:
        return ""
    return str(value).strip()[:max_length]
