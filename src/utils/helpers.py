"""
Helper utilities for the iMessage AI Support Agent.
"""

import uuid
import time
from datetime import datetime
from typing import Optional


def generate_conversation_id(prefix: str = "conv") -> str:
    """
    Generate a unique conversation ID.

    Args:
        prefix: Prefix for the conversation ID

    Returns:
        Unique conversation ID string
    """

    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]

    return f"{prefix}_{timestamp}_{unique_id}"


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format a timestamp into a human-readable string.

    Args:
        timestamp: Unix timestamp (defaults to current time)

    Returns:
        Formatted timestamp string
    """

    if timestamp is None:
        timestamp = time.time()

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds into a human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """

    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
    else:
        days = seconds / 86400
        return f"{days:.1f} days"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def safe_get_nested(data: dict, *keys, default=None):
    """
    Safely get nested dictionary values.

    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found

    Returns:
        Value at the specified path or default
    """

    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """

    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def generate_phone_mask(phone: str, mask_char: str = "*") -> str:
    """
    Generate a masked version of a phone number for privacy.

    Args:
        phone: Phone number to mask
        mask_char: Character to use for masking

    Returns:
        Masked phone number
    """

    if not phone:
        return phone

    # Remove non-digit characters
    digits = "".join(filter(str.isdigit, phone))

    if len(digits) < 4:
        return phone

    # Mask middle digits, keep first and last 2
    masked = digits[:2] + mask_char * (len(digits) - 4) + digits[-2:]

    return masked


def is_business_hours(timestamp: Optional[float] = None) -> bool:
    """
    Check if the given timestamp is during business hours.

    Args:
        timestamp: Unix timestamp (defaults to current time)

    Returns:
        True if during business hours (9 AM - 5 PM, Monday-Friday)
    """

    if timestamp is None:
        timestamp = time.time()

    dt = datetime.fromtimestamp(timestamp)

    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if dt.weekday() >= 5:
        return False

    # Check if it's between 9 AM and 5 PM
    hour = dt.hour
    return 9 <= hour < 17


def calculate_response_priority(
    urgency: str, customer_tier: str = "standard", business_hours: bool = None
) -> int:
    """
    Calculate response priority score (1-10).

    Args:
        urgency: Urgency level (low, medium, high, critical)
        customer_tier: Customer tier (standard, premium, vip)
        business_hours: Whether it's business hours

    Returns:
        Priority score from 1-10
    """

    # Base priority by urgency
    urgency_scores = {"low": 1, "medium": 3, "high": 6, "critical": 9}

    base_score = urgency_scores.get(urgency.lower(), 3)

    # Adjust by customer tier
    tier_multipliers = {"standard": 1.0, "premium": 1.5, "vip": 2.0}

    multiplier = tier_multipliers.get(customer_tier.lower(), 1.0)
    adjusted_score = base_score * multiplier

    # Adjust by business hours
    if business_hours is None:
        business_hours = is_business_hours()

    if not business_hours:
        adjusted_score *= 0.8  # Reduce priority outside business hours

    # Ensure score is within 1-10 range
    return max(1, min(10, int(adjusted_score)))
