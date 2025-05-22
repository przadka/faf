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

# Local application imports
from src.faf.main import load_configuration
# Import the MCP tools to ensure they are registered via decorators

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
        # FastAPI app is not needed for FastMCP, so remove it
        # self.app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION)
        self.mcp_server = mcp  # Use the shared instance
        logger.info(f"MCP Server initialized with model: {self.model}")

    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Run the MCP server.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        logger.info(f"Starting MCP Server on {host}:{port}")
        self.mcp_server.run(
            "streamable-http",  # Use HTTP transport
            host=host,
            port=port,
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

