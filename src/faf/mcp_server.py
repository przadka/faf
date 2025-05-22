#!/usr/bin/env python3
"""
MCP Server for FAF (Fire And Forget)

This module implements a Model Context Protocol (MCP) server for FAF,
enabling integration with MCP-compatible clients using the official MCP SDK.

Based on MCP Specification 2025-03-26: https://modelcontextprotocol.io/specification/2025-03-26
"""

import logging
import os
import sys

# Import MCP SDK
from fastmcp import FastMCP
from fastapi import FastAPI

# Local application imports
from src.faf.main import load_configuration
# Import the MCP tools directly - they're already decorated with @tool
from src.faf.mcp_tools import (
    follow_up_then,
    note_to_self,
    save_url,
    va_request,
    journaling_topic
)

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

        # Create MCP server - pass only name as recommended since 2.3.4
        self.mcp_server = FastMCP(SERVER_NAME)

        # Register tools using the decorator-based approach
        self._register_tools()

        logger.info(f"MCP Server initialized with model: {self.model}")

    def _register_tools(self):
        """Register FAF tools with the MCP server."""
        # In the current version of FastMCP, tools are registered using the decorator pattern
        # Add the tools to the tool manager by decorating them again

        @self.mcp_server.tool(name="follow_up_then", description=follow_up_then.__doc__)
        async def follow_up_then_wrapper(call):
            return await follow_up_then(call)

        @self.mcp_server.tool(name="note_to_self", description=note_to_self.__doc__)
        async def note_to_self_wrapper(call):
            return await note_to_self(call)

        @self.mcp_server.tool(name="save_url", description=save_url.__doc__)
        async def save_url_wrapper(call):
            return await save_url(call)

        @self.mcp_server.tool(name="va_request", description=va_request.__doc__)
        async def va_request_wrapper(call):
            return await va_request(call)

        @self.mcp_server.tool(name="journaling_topic", description=journaling_topic.__doc__)
        async def journaling_topic_wrapper(call):
            return await journaling_topic(call)

    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Run the MCP server.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        logger.info(f"Starting MCP Server on {host}:{port}")
        # Pass settings to run() as recommended since 2.3.4
        self.mcp_server.run(
            app=self.app,
            host=host,
            port=port,
            version=SERVER_VERSION,
            description=SERVER_DESCRIPTION
        )

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

