#!/usr/bin/env python3
"""
MCP Server for FAF (Fire And Forget)

This module implements a Model Context Protocol (MCP) server for FAF,
enabling integration with MCP-compatible clients using the official MCP SDK.

Based on MCP Specification 2025-03-26: https://modelcontextprotocol.io/specification/2025-03-26
"""

import json
import logging
import os
import sys

# Import MCP SDK
from mcp import FastMCP, MCPToolDefinition, MCPToolCall, MCPToolResult, MCPToolError
from fastapi import FastAPI, Request

# Local application imports
from src.faf.tools import follow_up_then, note_to_self, save_url, va_request, journaling_topic
from src.faf.main import get_tool_function_info, load_configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("faf_mcp_server")

# MCP server configuration
SERVER_NAME = "faf-mcp-server"
SERVER_VERSION = "0.1.0"

class FafMcpServer:
    """
    MCP Server implementation for FAF using the FastMCP SDK.

    This class implements an MCP server that provides FAF (Fire And Forget)
    tools as MCP tools for use by compatible clients.
    """

    def __init__(self):
        """Initialize the MCP server."""
        # Load FAF configuration
        self.model, self.user_name, self.custom_rules = load_configuration()

        # Create FastAPI app
        self.app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION)

        # Create MCP server
        self.mcp_server = FastMCP(
            app=self.app,
            server_name=SERVER_NAME,
            server_version=SERVER_VERSION
        )

        # Register tools
        self._register_tools()

        logger.info(f"MCP Server initialized with model: {self.model}")

    def _register_tools(self):
        """Register FAF tools with the MCP server."""
        # Register follow_up_then tool
        self.mcp_server.register_tool(
            self._create_tool_definition(follow_up_then),
            self._create_tool_handler(follow_up_then)
        )

        # Register note_to_self tool
        self.mcp_server.register_tool(
            self._create_tool_definition(note_to_self),
            self._create_tool_handler(note_to_self)
        )

        # Register save_url tool
        self.mcp_server.register_tool(
            self._create_tool_definition(save_url),
            self._create_tool_handler(save_url)
        )

        # Register va_request tool
        self.mcp_server.register_tool(
            self._create_tool_definition(va_request),
            self._create_tool_handler(va_request)
        )

        # Register journaling_topic tool
        self.mcp_server.register_tool(
            self._create_tool_definition(journaling_topic),
            self._create_tool_handler(journaling_topic)
        )

    def _create_tool_definition(self, func) -> MCPToolDefinition:
        """
        Create an MCP tool definition from a FAF tool function.

        Args:
            func: The FAF tool function

        Returns:
            MCPToolDefinition for the tool
        """
        # Get function signature and docstring information
        faf_tool_info = get_tool_function_info(func)

        # Create parameter schema for MCP tool
        parameters = {
            "type": "object",
            "properties": {},
            "required": faf_tool_info["function"]["parameters"]["required"]
        }

        # Convert parameters
        for name, param_info in faf_tool_info["function"]["parameters"]["properties"].items():
            parameters["properties"][name] = {
                "type": param_info["type"],
                "description": param_info["description"]
            }

        # Create and return the tool definition
        return MCPToolDefinition(
            name=faf_tool_info["function"]["name"],
            description=faf_tool_info["function"]["description"],
            parameters=parameters
        )

    def _create_tool_handler(self, func):
        """
        Create an MCP tool handler function for a FAF tool function.

        Args:
            func: The FAF tool function

        Returns:
            Async function that handles the tool call
        """
        async def tool_handler(call: MCPToolCall, request: Request) -> MCPToolResult:
            try:
                # Execute the FAF tool function with the provided arguments
                arguments = call.arguments

                # Call the tool function
                result = func(**arguments)

                # Parse the result (which is a JSON string) to get the tool output
                result_dict = json.loads(result)

                # Return a successful result
                return MCPToolResult(result=result_dict)
            except Exception as e:
                # Log and return an error
                logger.exception(f"Error executing tool {func.__name__}: {e}")
                raise MCPToolError(message=str(e))

        return tool_handler

    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Run the MCP server.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        import uvicorn
        logger.info(f"Starting MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """Main entry point for the MCP server."""
    try:
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='FAF MCP Server')
        parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
        parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
        args = parser.parse_args()

        # Load environment variables
        import dotenv
        dotenv.load_dotenv()

        # Ensure required environment variables are set
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY environment variable not set")
            sys.exit(1)

        # Create and run the server
        server = FafMcpServer()
        server.run(args.host, args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
