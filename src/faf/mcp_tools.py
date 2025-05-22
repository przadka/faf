"""
MCP Tools for FAF (Fire And Forget)

This module wraps the FAF tools with MCP decorators to make them available via the MCP server.
"""

import re

from mcp import tool
from mcp.types import MCPToolCall, MCPToolResult


@tool
async def follow_up_then(call: MCPToolCall) -> MCPToolResult:
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
    prompt = call.arguments.get("prompt", "")
    date = call.arguments.get("date", "")
    message = call.arguments.get("message", "")

    # Format the date
    date = date.replace("this", "")
    date = date.replace(" ", "")
    date = date.replace(".", "")
    date = date.replace(",", "")
    date = date.replace(":", "")

    # Remove "in" if used as "inXday" or "inXweek" or "inXmonth", match the number and the unit
    date = re.sub(r'in(\d+)(day|week|month)', r'\1\2', date)

    tool_data = {
        "prompt": prompt,
        "command": "follow_up_then",
        "payload": {
            "date": date,
            "message": message
        }
    }

    return MCPToolResult(result=tool_data)


@tool
async def note_to_self(call: MCPToolCall) -> MCPToolResult:
    """
    Send a note to user with the given message.
    Useful for simple todos, reminders and short-term follow ups.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        message: Message to send. Should be based on the prompt, without any additional information.

    Returns:
        Tool result with structured data.
    """
    prompt = call.arguments.get("prompt", "")
    message = call.arguments.get("message", "")

    tool_data = {
        "prompt": prompt,
        "command": "note_to_self",
        "payload": {
            "message": message
        }
    }

    return MCPToolResult(result=tool_data)


@tool
async def save_url(call: MCPToolCall) -> MCPToolResult:
    """
    Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        url: URL to append to the URL list.

    Returns:
        Tool result with structured data.
    """
    prompt = call.arguments.get("prompt", "")
    url = call.arguments.get("url", "")

    # Check if the input is URL-like
    if not url.startswith("http") or "." not in url or " " in url:
        raise ValueError("The input is not a valid URL.")

    tool_data = {
        "prompt": prompt,
        "command": "save_url",
        "payload": {
            "url": url
        }
    }

    return MCPToolResult(result=tool_data)


@tool
async def journaling_topic(call: MCPToolCall) -> MCPToolResult:
    """
    Save a journaling topic to the idea list, to write about later.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        topic: Topic to save, with any relevant details.

    Returns:
        Tool result with structured data.
    """
    prompt = call.arguments.get("prompt", "")
    topic = call.arguments.get("topic", "")

    tool_data = {
        "prompt": prompt,
        "command": "journaling_topic",
        "payload": {
            "topic": topic
        }
    }

    return MCPToolResult(result=tool_data)


@tool
async def va_request(call: MCPToolCall) -> MCPToolResult:
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
    prompt = call.arguments.get("prompt", "")
    title = call.arguments.get("title", "")
    request = call.arguments.get("request", "")

    tool_data = {
        "prompt": prompt,
        "command": "va_request",
        "payload": {
            "title": title,
            "request": request
        }
    }

    return MCPToolResult(result=tool_data)

