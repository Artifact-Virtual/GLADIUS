"""
Validation utilities for business infrastructure.

Provides common validation functions.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional


def validate_currency_code(currency: str) -> bool:
    """
    Validate currency code format.
    
    Args:
        currency: Currency code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not currency or not isinstance(currency, str):
        return False
    
    return len(currency) == 3 and currency.isalpha()


def validate_symbol(symbol: str, max_length: int = 20) -> bool:
    """
    Validate asset symbol format.
    
    Args:
        symbol: Symbol to validate
        max_length: Maximum allowed length
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Allow alphanumeric and common symbols
    pattern = r'^[A-Z0-9\-\.\_]+$'
    return bool(re.match(pattern, symbol.upper())) and len(symbol) <= max_length


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_positive_decimal(value: Any) -> bool:
    """
    Validate that value is a positive decimal.
    
    Args:
        value: Value to validate
        
    Returns:
        True if valid positive decimal, False otherwise
    """
    try:
        decimal_value = Decimal(str(value))
        return decimal_value > 0
    except (InvalidOperation, ValueError, TypeError):
        return False


def validate_non_negative_decimal(value: Any) -> bool:
    """
    Validate that value is a non-negative decimal.
    
    Args:
        value: Value to validate
        
    Returns:
        True if valid non-negative decimal, False otherwise
    """
    try:
        decimal_value = Decimal(str(value))
        return decimal_value >= 0
    except (InvalidOperation, ValueError, TypeError):
        return False


def validate_string_length(value: str, min_length: int = 1, max_length: int = 255) -> bool:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, str):
        return False
    
    length = len(value.strip())
    return min_length <= length <= max_length


def validate_list_contains(value: Any, allowed_values: List[Any]) -> bool:
    """
    Validate that value is in allowed values list.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        
    Returns:
        True if value in list, False otherwise
    """
    return value in allowed_values


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by trimming and limiting length.
    
    Args:
        value: String to sanitize
        max_length: Maximum length (no limit if None)
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    sanitized = value.strip()
    
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    return f"{currency} {amount:,.2f}"


def format_percentage(value: Decimal, decimal_places: int = 2) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"
