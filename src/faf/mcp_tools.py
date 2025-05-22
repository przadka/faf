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

import anyio.to_thread
from mcp.types import CallToolRequestParams as MCPToolCall

# Define our own MCPToolResult since it's not available in mcp.types
class MCPToolResult:
    """Result of a tool call."""

    def __init__(self, result: Dict[str, Any]):
        self.result = result

# Create a tool decorator since it's not directly available
def tool(func: Callable[..., Awaitable[MCPToolResult]]) -> Callable[..., Awaitable[MCPToolResult]]:
    """Decorator to mark a function as an MCP tool."""
    @functools.wraps(func)
    async def wrapper(call: MCPToolCall) -> MCPToolResult:
        return await func(call)

    # Store the original function for later registration
    wrapper.__mcp_tool__ = True
    return wrapper


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

    # Offload the synchronous function call to a thread pool
    result_json = await anyio.to_thread.run_sync(
        follow_up_then_sync, prompt, date, message
    )

    # Parse the JSON string result
    result_dict = json.loads(result_json)

    return MCPToolResult(result=result_dict)


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

    # Offload the synchronous function call to a thread pool
    result_json = await anyio.to_thread.run_sync(
        note_to_self_sync, prompt, message
    )

    # Parse the JSON string result
    result_dict = json.loads(result_json)

    return MCPToolResult(result=result_dict)


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

    # Offload the synchronous function call to a thread pool
    result_json = await anyio.to_thread.run_sync(
        save_url_sync, prompt, url
    )

    # Check for error response
    if result_json.startswith("Error:"):
        raise ValueError(result_json)

    # Parse the JSON string result
    result_dict = json.loads(result_json)

    return MCPToolResult(result=result_dict)


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

    # Offload the synchronous function call to a thread pool
    result_json = await anyio.to_thread.run_sync(
        journaling_topic_sync, prompt, topic
    )

    # Parse the JSON string result
    result_dict = json.loads(result_json)

    return MCPToolResult(result=result_dict)


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

    # Offload the synchronous function call to a thread pool
    result_json = await anyio.to_thread.run_sync(
        va_request_sync, prompt, title, request
    )

    # Parse the JSON string result
    result_dict = json.loads(result_json)

    return MCPToolResult(result=result_dict)

