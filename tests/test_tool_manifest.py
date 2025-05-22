"""
Test that the MCP tools are correctly registered with the expected names.
"""

from src.faf.mcp_server import FafMcpServer

def test_tool_manifest():
    """Test that all expected tools are registered in the MCP server."""
    # Create an instance of the MCP server
    server = FafMcpServer()

    # Expected tool names
    expected_tools = [
        'follow_up_then',
        'note_to_self',
        'save_url',
        'va_request',
        'journaling_topic'
    ]

    # Get the registered tools
    # Access the tools through the server instance
    registered_tool_names = [tool.name for tool in server.mcp_server.tools]

    # Check that all expected tools are registered
    for expected_tool in expected_tools:
        assert expected_tool in registered_tool_names, \
            f"Tool {expected_tool} not found in registered tools"

    # Check that we have exactly the expected number of tools
    assert len(registered_tool_names) == len(expected_tools), \
        f"Expected {len(expected_tools)} tools, but found {len(registered_tool_names)}"

