import json
import pytest
from unittest import mock
from unittest.mock import Mock, patch, MagicMock
from faf.mcp_server import FafMcpServer


class TestFafMcpServer:
    """Test cases for the FAF MCP Server."""

    @patch('faf.mcp_server.load_configuration')
    def test_init(self, mock_load_config):
        """Test that FafMcpServer initializes correctly."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
        
        server = FafMcpServer()
        
        assert server.model == "gpt-4o"
        assert server.user_name == "TestUser"
        assert server.custom_rules == "Custom rules"
        mock_load_config.assert_called_once()

    @patch('faf.mcp_server.load_configuration')
    @patch('faf.mcp_server.mcp')
    def test_run_stdio(self, mock_mcp, mock_load_config):
        """Test that run_stdio calls FastMCP with correct transport."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
        mock_mcp.run = Mock()
        
        server = FafMcpServer()
        server.run_stdio()
        
        mock_mcp.run.assert_called_once_with(transport="stdio")

    @patch('faf.mcp_server.load_configuration')
    @patch('faf.mcp_server.uvicorn')
    @patch('faf.mcp_server.FastAPI')
    @patch('faf.mcp_server.mcp')
    def test_run_http(self, mock_mcp, mock_fastapi, mock_uvicorn, mock_load_config):
        """Test that run_http starts FastAPI server with correct parameters."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
        mock_app = Mock()
        mock_fastapi.return_value = mock_app
        mock_mcp.streamable_http_app.return_value = Mock()
        
        server = FafMcpServer()
        server.run_http("localhost", 8000)
        
        mock_fastapi.assert_called_once()
        mock_uvicorn.run.assert_called_once_with(mock_app, host="localhost", port=8000)

    @patch('faf.mcp_server.load_configuration')
    @patch('faf.mcp_server.uvicorn')
    @patch('faf.mcp_server.FastAPI')
    @patch('faf.mcp_server.mcp')
    def test_run_http_default_args(self, mock_mcp, mock_fastapi, mock_uvicorn, mock_load_config):
        """Test that run_http uses default host and port when not specified."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
        mock_app = Mock()
        mock_fastapi.return_value = mock_app
        mock_mcp.streamable_http_app.return_value = Mock()
        
        server = FafMcpServer()
        server.run_http()
        
        mock_uvicorn.run.assert_called_once_with(mock_app, host="127.0.0.1", port=5000)


class TestMcpServerIntegration:
    """Integration tests for MCP server functionality."""

    def test_server_creation(self):
        """Test that server can be created without errors."""
        with patch('faf.mcp_server.load_configuration') as mock_load_config:
            mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
            server = FafMcpServer()
            assert server is not None

    def test_help_output(self):
        """Test that the server shows help correctly."""
        import subprocess
        import sys
        
        # Run the server with --help flag
        result = subprocess.run([
            sys.executable, '-m', 'faf.mcp_server', '--help'
        ], capture_output=True, text=True, cwd='/home/michal/dev/faf/src')
        
        assert result.returncode == 0
        assert 'FAF MCP Server' in result.stdout
        assert '--transport' in result.stdout
        assert 'stdio' in result.stdout
        assert 'http' in result.stdout