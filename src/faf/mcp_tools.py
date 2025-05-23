"""
MCP Tools for FAF (Fire And Forget)

This module wraps the FAF tools with MCP decorators to make them available via the MCP server.
Includes comprehensive input validation and error handling.
"""

import json
from functools import wraps
from typing import Optional

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

# Import validation functions
from faf.validation import (
    validate_non_empty_string,
    validate_url,
    validate_date_format,
    validate_priority,
    validate_va_keywords,
)

# Import the shared FastMCP instance
from faf.mcp_server import mcp



@mcp.tool()
@wraps(follow_up_then_sync)
async def follow_up_then(prompt: str, date: str, message: str) -> dict:
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
@wraps(note_to_self_sync)
async def note_to_self(prompt: str, message: str, priority: Optional[str] = "normal") -> dict:
    # Add debugging
    import logging
    logger = logging.getLogger("faf_mcp_tools")
    logger.info(
        f"note_to_self called with prompt='{prompt}', message='{message}', priority='{priority}'"
    )

    # Input validation
    validate_non_empty_string(prompt, "Prompt")
    validate_non_empty_string(message, "Message")

    if priority is not None:
        validate_priority(priority)

    # For now, we'll ignore the priority parameter in the sync call to maintain
    # backward compatibility
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
@wraps(save_url_sync)
async def save_url(prompt: str, url: str) -> dict:
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
@wraps(journaling_topic_sync)
async def journaling_topic(prompt: str, topic: str, category: Optional[str] = None) -> dict:
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
@wraps(va_request_sync)
async def va_request(
    prompt: str, title: str, request: str, urgency: Optional[str] = "normal"
) -> dict:
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
        raise ValueError(
            "Title should be short (100 characters or less) for Trello card compatibility"
        )

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

