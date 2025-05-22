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

        # Register tools using the decorator-based approach
        self._register_tools()

        logger.info(f"MCP Server initialized with model: {self.model}")

    def _register_tools(self):
        """Register FAF tools with the MCP server."""
        # Register all tools that have been decorated with @tool
        self.mcp_server.register_tool(follow_up_then)
        self.mcp_server.register_tool(note_to_self)
        self.mcp_server.register_tool(save_url)
        self.mcp_server.register_tool(va_request)
        self.mcp_server.register_tool(journaling_topic)

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

