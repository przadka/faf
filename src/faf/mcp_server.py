#!/usr/bin/env python3
"""
MCP Server for FAF (Fire And Forget)

This module implements a Model Context Protocol (MCP) server for FAF,
enabling integration with MCP-compatible clients using the official MCP SDK.
Supports both stdio (for local development/desktop clients) and HTTP transports.

Based on MCP Specification 2025-03-26: https://modelcontextprotocol.io/specification/2025-03-26
"""

import logging
import os
import sys

# Import MCP SDK
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn

# Local application imports
from faf.main import load_configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("faf_mcp_server")

# MCP server configuration
SERVER_NAME = "faf-mcp-server"
SERVER_VERSION = "0.1.0"
SERVER_DESCRIPTION = "MCP server for Fire And Forget (FAF) command-line tool"

# Create the FastMCP instance at the module level for use by decorators
mcp = FastMCP(SERVER_NAME)

# Import the MCP tools to ensure they are registered via decorators
import faf.mcp_tools  # noqa: F401, E402, registers all @mcp.tool decorators

class FafMcpServer:
    """
    MCP Server implementation for FAF using the FastMCP SDK.

    This class implements an MCP server that provides FAF (Fire And Forget)
    tools as MCP tools for use by compatible clients. Supports both stdio
    and HTTP transports.
    """

    def __init__(self):
        """Initialize the MCP server."""
        # Load FAF configuration
        self.model, self.user_name, self.custom_rules = load_configuration()
        self.mcp_server = mcp  # Use the shared instance
        logger.info(f"MCP Server initialized with model: {self.model}")

    def run_stdio(self):
        """
        Run the MCP server using stdio transport.

        This is the preferred method for local development and desktop clients
        like Claude Desktop and VS Code extensions.
        """
        logger.info("Starting MCP Server with stdio transport")

        # Run the stdio server using FastMCP's built-in functionality
        # FastMCP.run() creates its own event loop, so we don't need async here
        self.mcp_server.run(transport="stdio")

    def run_http(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Run the MCP server using HTTP transport.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        logger.info(f"Starting MCP Server with HTTP transport on {host}:{port}")
        # Create a new FastAPI app
        app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION, description=SERVER_DESCRIPTION)

        # Mount the FastMCP app to a specific path
        from starlette.routing import Mount

        # Get the streamable HTTP app from FastMCP and add it to the main app
        mcp_app = self.mcp_server.streamable_http_app()

        # Add some additional routes for status/health checks if needed
        @app.get("/health")
        async def health_check():
            return {"status": "ok"}

        # Include the MCP app
        app.routes.append(Mount("/mcp", app=mcp_app))

        # Start the Uvicorn server with our app
        uvicorn.run(app, host=host, port=port)

def main():
    """Main entry point for the MCP server."""
    try:
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='FAF MCP Server')
        parser.add_argument('--transport', choices=['stdio', 'http'], default='stdio',
                          help='Transport protocol to use (default: stdio)')
        parser.add_argument('--host', default='127.0.0.1',
                          help='Host to bind to (HTTP transport only)')
        parser.add_argument('--port', type=int, default=5000,
                          help='Port to listen on (HTTP transport only)')
        args = parser.parse_args()

        # Load environment variables
        import dotenv
        dotenv.load_dotenv()

        # Ensure required environment variables are set
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY environment variable not set")
            sys.exit(1)

        # Create the server
        server = FafMcpServer()

        # Run the appropriate transport
        if args.transport == 'stdio':
            server.run_stdio()
        else:
            server.run_http(args.host, args.port)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

