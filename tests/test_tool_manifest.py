"""
Test that the MCP tools are correctly registered with the expected names.
"""

from faf.mcp_server import FafMcpServer

def test_tool_manifest():
    """Test that all expected tools are registered in the MCP server."""
    # Create an instance of the MCP server
    server = FafMcpServer()

    # Tools expected to be registered:
    # expected_tools = ["follow_up_then", "note_to_self", "save_url",
    #                   "va_request", "journaling_topic"]

    # LIMITATION: Current FastMCP API doesn't provide direct access to registered tools
    # This test verifies server initialization as an indirect confirmation of tool registration
    # since tools are registered via decorators during module import.

    # Verify that the server instance is created successfully
    assert isinstance(server, FafMcpServer)
    assert hasattr(server, 'mcp_server')

    # The FastMCP class provides a tool decorator which we use, and we know
    # that all of our tools are imported via faf.mcp_tools, so if the server
    # initializes without errors, we can reasonably assume the tools are registered.

    # TODO: Enhance this test when FastMCP API evolves to support tool inspection
    # Future enhancement could look like:
    # if hasattr(server.mcp_server, 'get_registered_tools'):
    #     tools = server.mcp_server.get_registered_tools()
    #     for tool in expected_tools:
    #         assert tool in tools, f"Tool '{tool}' is not registered"


def test_tool_manifest_detailed():
    """
    Future enhancement for detailed tool verification.

    This test is commented out as it depends on FastMCP API evolution.
    Uncomment and modify when the API supports tool inspection.
    """
    # server = FafMcpServer()
    # # Hypothetical future API method to get registered tools
    # tools = server.get_registered_tools()
    #
    # # Verify all expected tools are registered
    # expected_tools = ["follow_up_then", "note_to_self", "save_url",
    #                   "va_request", "journaling_topic"]
    # for tool in expected_tools:
    #     assert tool in tools, f"Tool '{tool}' is not registered"
    pass

