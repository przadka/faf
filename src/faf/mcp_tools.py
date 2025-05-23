"""
MCP Tools for FAF (Fire And Forget)

This module wraps the FAF tools with MCP decorators to make them available via the MCP server.
Includes comprehensive input validation and error handling.
"""

import json
from typing import Optional
from urllib.parse import urlparse

# Import the original synchronous FAF tool functions
from faf.tools import (
    follow_up_then as follow_up_then_sync,
    note_to_self as note_to_self_sync,
    save_url as save_url_sync,
    va_request as va_request_sync,
    journaling_topic as journaling_topic_sync,
)

# Import the write_to_file function to actually save JSON files
from faf.main import write_to_file

# Import the shared FastMCP instance
from faf.mcp_server import mcp


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
        raise ValueError("VA requests must include 'virtual assistant', 'v assistant', or 'VA' in the prompt")

@mcp.tool()
async def follow_up_then(prompt: str, date: str, message: str) -> dict:
    """
    Send a follow-up reminder with the given date and message.
    Use ONLY IF there is a specific date provided or
    a time reference, like "tomorrow" or "in 2 days".

    Constraints on the date:
      - Never use "this" in the date like "thisMonday" or "thisTuesday" as FUT does not
        support them.
      - Never use "in a week", "in two weeks" or "in a month" replace them with "1week",
        "2weeks" and "1month" respectively.
      - Date cannot have any spaces, dots, semicolons or commas.
      - Never use colons in hours, use "3pm" instead of "3:00pm".

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        date: Date of the follow-up in the format like "1August", "tomorrow3pm" or "in2days".
        message: Message to send. Do not include the date in the message.

    Returns:
        Tool result with structured data.
    """
    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_non_empty_string(date, "Date")
    validate_non_empty_string(message, "Message")
    validate_date_format(date)

    result_json = follow_up_then_sync(prompt, date, message)
    result_dict = json.loads(result_json)

    # Save the JSON file to disk
    try:
        save_result = write_to_file(result_json)
        print(f"File saved: {save_result}")
    except Exception as e:
        print(f"Failed to save file: {e}")

    return result_dict


@mcp.tool()
async def note_to_self(prompt: str, message: str, priority: Optional[str] = "normal") -> dict:
    """
    Send a note to user with the given message and optional priority level.
    Useful for simple to-dos, reminders and short-term follow ups.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        message: Message to send. Should be based on the prompt, without any additional information.
        priority: Priority level for the note (low, normal, high). Defaults to "normal".

    Returns:
        Tool result with structured data.
    """
    # Add debugging
    import logging
    logger = logging.getLogger("faf_mcp_tools")
    logger.info(f"note_to_self called with prompt='{prompt}', message='{message}', priority='{priority}'")

    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_non_empty_string(message, "Message")

    if priority is not None:
        validate_priority(priority)

    # For now, we'll ignore the priority parameter in the sync call to maintain backward compatibility
    # but the validation ensures proper input
    logger.info("Calling note_to_self_sync...")
    result_json = note_to_self_sync(prompt, message)
    logger.info(f"note_to_self_sync returned: {result_json}")
    result_dict = json.loads(result_json)

    # Add priority to the result if specified
    if priority and priority != "normal":
        result_dict["payload"]["priority"] = priority

    # Save the JSON file to disk
    try:
        updated_json = json.dumps(result_dict)
        save_result = write_to_file(updated_json)
        logger.info(f"File saved: {save_result}")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")

    logger.info(f"Returning result: {result_dict}")
    return result_dict


@mcp.tool()
async def save_url(prompt: str, url: str) -> dict:
    """
    Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        url: URL to append to the URL list.

    Returns:
        Tool result with structured data.
    """
    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_url(url)

    result_json = save_url_sync(prompt, url)
    if result_json.startswith("Error:"):
        raise ValueError(result_json)

    result_dict = json.loads(result_json)

    # Save the JSON file to disk
    try:
        save_result = write_to_file(result_json)
        print(f"File saved: {save_result}")
    except Exception as e:
        print(f"Failed to save file: {e}")

    return result_dict


@mcp.tool()
async def journaling_topic(prompt: str, topic: str, category: Optional[str] = None) -> dict:
    """
    Save a journaling topic to the idea list, to write about later.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        topic: Topic to save, with any relevant details.
        category: Optional category for organizing topics (e.g., "personal", "work", "reflection").

    Returns:
        Tool result with structured data.
    """
    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_non_empty_string(topic, "Topic")

    if category is not None:
        validate_non_empty_string(category, "Category")

    result_json = journaling_topic_sync(prompt, topic)
    result_dict = json.loads(result_json)

    # Add category to the result if specified
    if category:
        result_dict["payload"]["category"] = category

    # Save the JSON file to disk
    try:
        updated_json = json.dumps(result_dict)
        save_result = write_to_file(updated_json)
        print(f"File saved: {save_result}")
    except Exception as e:
        print(f"Failed to save file: {e}")

    return result_dict


@mcp.tool()
async def va_request(prompt: str, title: str, request: str, urgency: Optional[str] = "normal") -> dict:
    """
    Send a request to the VA with the given message. Use only if the input explicitly asks for a
    virtual assistant or VA. Use ONLY if the prompt includes the words "virtual assistant",
    "v assistant" or "VA".

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        title: Title of the request, used as a Trello card title. Keep it short.
        request: Request to send.
        urgency: Urgency level for the request (low, normal, high, urgent). Defaults to "normal".

    Returns:
        Tool result with structured data.
    """
    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_non_empty_string(title, "Title")
    validate_non_empty_string(request, "Request")
    validate_va_keywords(prompt)

    # Validate urgency if provided
    if urgency is not None:
        valid_urgencies = ["low", "normal", "high", "urgent"]
        if urgency not in valid_urgencies:
            raise ValueError(f"Urgency must be one of: {', '.join(valid_urgencies)}")

    # Validate title length (should be short for Trello card)
    if len(title) > 100:
        raise ValueError("Title should be short (100 characters or less) for Trello card compatibility")

    result_json = va_request_sync(prompt, title, request)
    result_dict = json.loads(result_json)

    # Add urgency to the result if specified
    if urgency and urgency != "normal":
        result_dict["payload"]["urgency"] = urgency

    # Save the JSON file to disk
    try:
        updated_json = json.dumps(result_dict)
        save_result = write_to_file(updated_json)
        print(f"File saved: {save_result}")
    except Exception as e:
        print(f"Failed to save file: {e}")

    return result_dict

