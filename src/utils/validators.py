"""
Validation utilities for the iMessage AI Support Agent.
"""

import re
from typing import Optional, Tuple


def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a phone number format.

    Args:
        phone: Phone number string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """

    if not phone:
        return False, "Phone number cannot be empty"

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Check if it's a valid length (7-15 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return False, f"Phone number must be 7-15 digits, got {len(digits_only)}"

    # Check if it starts with a valid country code or area code
    if len(digits_only) >= 10:
        # US/Canada format: +1 (555) 123-4567
        if digits_only.startswith("1") and len(digits_only) == 11:
            return True, None
        elif len(digits_only) == 10:
            return True, None
        else:
            return True, None  # Assume international format

    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address format.

    Args:
        email: Email string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """

    if not email:
        return False, "Email cannot be empty"

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email format"

    # Check for common issues
    if email.count("@") != 1:
        return False, "Email must contain exactly one @ symbol"

    if email.startswith(".") or email.endswith("."):
        return False, "Email cannot start or end with a dot"

    if ".." in email:
        return False, "Email cannot contain consecutive dots"

    return True, None


def validate_conversation_id(conversation_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a conversation ID format.

    Args:
        conversation_id: Conversation ID string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """

    if not conversation_id:
        return False, "Conversation ID cannot be empty"

    # Check length (should be reasonable)
    if len(conversation_id) < 3 or len(conversation_id) > 100:
        return (
            False,
            f"Conversation ID must be 3-100 characters, got {len(conversation_id)}",
        )

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9_-]+$", conversation_id):
        return (
            False,
            "Conversation ID can only contain letters, numbers, hyphens, and underscores",
        )

    return True, None


def validate_message_content(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate message content.

    Args:
        content: Message content string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """

    if not content:
        return False, "Message content cannot be empty"

    # Check length
    if len(content) > 10000:  # 10KB limit
        return False, "Message content too long (max 10,000 characters)"

    # Check for potentially harmful content
    harmful_patterns = [
        r"<script.*?>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"data:text/html",  # Data URLs
        r"vbscript:",  # VBScript protocol
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, "Message content contains potentially harmful content"

    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """

    if not text:
        return text

    # Remove or escape potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&"]
    replacements = ["&lt;", "&gt;", "&quot;", "&#39;", "&amp;"]

    sanitized = text
    for char, replacement in zip(dangerous_chars, replacements):
        sanitized = sanitized.replace(char, replacement)

    return sanitized


def validate_webhook_signature(
    payload: str, signature: str, secret: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate webhook signature for security.

    Args:
        payload: Raw payload string
        signature: Signature header value
        secret: Webhook secret key

    Returns:
        Tuple of (is_valid, error_message)
    """

    if not signature:
        return False, "Missing webhook signature"

    if not secret:
        return False, "Missing webhook secret"

    # In a real implementation, you would:
    # 1. Generate HMAC hash of payload using secret
    # 2. Compare with signature header
    # 3. Check timestamp for replay attacks

    # For now, return a placeholder implementation
    return True, None
