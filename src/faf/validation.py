"""
Validation utilities for FAF (Fire And Forget)

This module provides reusable validation functions that can be used across
different FAF interfaces (CLI, MCP, Lambda) to ensure data integrity and
provide appropriate error messages.
"""

from urllib.parse import urlparse


def validate_non_empty_string(value: str, field_name: str) -> None:
    """Validate that a string is not empty or only whitespace."""
    if not value or len(value.strip()) == 0:
        raise ValueError(f"{field_name} cannot be empty")


def validate_url(url: str) -> None:
    """Validate that a string is a properly formatted URL."""
    if not url or len(url.strip()) == 0:
        raise ValueError("URL cannot be empty")

    url = url.strip()

    # Basic URL format validation
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    if " " in url:
        raise ValueError("URL cannot contain spaces")

    if "." not in url:
        raise ValueError("URL must contain a domain with a dot")

    # Use urllib.parse for more thorough validation
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")
    except Exception:
        raise ValueError("Invalid URL format")


def validate_date_format(date: str) -> None:
    """Validate date format according to FUT constraints."""
    if not date or len(date.strip()) == 0:
        raise ValueError("Date cannot be empty")

    date = date.strip()

    # Check for forbidden characters and patterns
    forbidden_chars = [" ", ".", ",", ";"]
    for char in forbidden_chars:
        if char in date:
            raise ValueError(f"Date cannot contain '{char}' characters")

    # Check for forbidden "this" prefix
    if date.lower().startswith("this"):
        raise ValueError("Date cannot start with 'this' (use specific dates instead)")

    # Check for colon in time (should use 3pm not 3:00pm)
    if ":" in date:
        raise ValueError("Time should not contain colons (use '3pm' instead of '3:00pm')")

    # Check for invalid time expressions
    invalid_patterns = ["in a week", "in two weeks", "in a month"]
    date_lower = date.lower()
    for pattern in invalid_patterns:
        if pattern in date_lower:
            raise ValueError(f"Use '1week', '2weeks', '1month' instead of '{pattern}'")


def validate_priority(priority: str) -> None:
    """Validate priority level."""
    valid_priorities = ["low", "normal", "high"]
    if priority not in valid_priorities:
        raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")


def validate_va_keywords(prompt: str) -> None:
    """Validate that prompt contains VA-related keywords."""
    prompt_lower = prompt.lower()
    va_keywords = ["virtual assistant", "v assistant", "va"]

    if not any(keyword in prompt_lower for keyword in va_keywords):
        raise ValueError(
            "VA requests must include 'virtual assistant', 'v assistant', or 'VA' in the prompt"
        )
