"""
MCP Tools for FAF (Fire And Forget)

This module wraps the FAF tools with MCP decorators to make them available via the MCP server.
"""

import json
import functools
from typing import Any, Callable, Awaitable, Dict

# Import the original synchronous FAF tool functions
from src.faf.tools import (
    follow_up_then as follow_up_then_sync,
    note_to_self as note_to_self_sync,
    save_url as save_url_sync,
    va_request as va_request_sync,
    journaling_topic as journaling_topic_sync,
)

# Import the shared FastMCP instance
from src.faf.mcp_server import mcp

# Remove custom decorator, MCPToolResult, and manual thread-pool offloading

@mcp.tool()
async def follow_up_then(call: dict) -> dict:
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
    prompt = call.get("prompt", "")
    date = call.get("date", "")
    message = call.get("message", "")
    result_json = follow_up_then_sync(prompt, date, message)
    return json.loads(result_json)


@mcp.tool()
async def note_to_self(call: dict) -> dict:
    """
    Send a note to user with the given message.
    Useful for simple todos, reminders and short-term follow ups.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        message: Message to send. Should be based on the prompt, without any additional information.

    Returns:
        Tool result with structured data.
    """
    prompt = call.get("prompt", "")
    message = call.get("message", "")
    result_json = note_to_self_sync(prompt, message)
    return json.loads(result_json)


@mcp.tool()
async def save_url(call: dict) -> dict:
    """
    Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        url: URL to append to the URL list.

    Returns:
        Tool result with structured data.
    """
    prompt = call.get("prompt", "")
    url = call.get("url", "")
    result_json = save_url_sync(prompt, url)
    if result_json.startswith("Error:"):
        raise ValueError(result_json)
    return json.loads(result_json)


@mcp.tool()
async def journaling_topic(call: dict) -> dict:
    """
    Save a journaling topic to the idea list, to write about later.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        topic: Topic to save, with any relevant details.

    Returns:
        Tool result with structured data.
    """
    prompt = call.get("prompt", "")
    topic = call.get("topic", "")
    result_json = journaling_topic_sync(prompt, topic)
    return json.loads(result_json)


@mcp.tool()
async def va_request(call: dict) -> dict:
    """
    Send a request to the VA with the given message. Use only if the input explicitly asks for a
    virtual assistant or VA. Use ONLY if the prompt includes the words "virtual assistant",
    "v assistant" or "VA".

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        title: Title of the request, used as a Trello card title. Keep it short.
        request: Request to send.

    Returns:
        Tool result with structured data.
    """
    prompt = call.get("prompt", "")
    title = call.get("title", "")
    request = call.get("request", "")
    result_json = va_request_sync(prompt, title, request)
    return json.loads(result_json)

