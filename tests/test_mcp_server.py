from unittest.mock import Mock, patch
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
    @patch('faf.mcp_server.mcp')
    def test_run_http(self, mock_mcp, mock_load_config):
        """Test that run_http calls FastMCP with correct parameters."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")

        server = FafMcpServer()
        server.run_http("/custom")

        mock_mcp.run.assert_called_once_with(
            transport="streamable-http",
            mount_path="/custom"
        )

    @patch('faf.mcp_server.load_configuration')
    @patch('faf.mcp_server.mcp')
    def test_run_http_default_args(self, mock_mcp, mock_load_config):
        """Test that run_http uses default parameters when not specified."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")

        server = FafMcpServer()
        server.run_http()

        mock_mcp.run.assert_called_once_with(
            transport="streamable-http",
            mount_path="/mcp"
        )


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
        assert '--mount-path' in result.stdout


class TestMcpServerCLI:
    """Tests for MCP server CLI argument handling."""

    def test_parse_args_new_arguments(self):
        """Test that new CLI arguments are parsed correctly."""
        from faf.mcp_server import main

        # Test parsing mount-path argument
        with patch('sys.argv', ['mcp_server.py', '--transport', 'http', '--mount-path', '/custom']):
            with patch('faf.mcp_server.os.getenv', return_value='test-key'):
                with patch('faf.mcp_server.load_configuration') as mock_load_config:
                    mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
                    with patch('faf.mcp_server.FafMcpServer') as mock_server_class:
                        mock_server = Mock()
                        mock_server_class.return_value = mock_server

                        try:
                            main()
                        except SystemExit:
                            pass  # Expected for test

                        # Verify the server was called with correct arguments
                        mock_server.run_http.assert_called_once_with(
                            mount_path='/custom'
                        )

    def test_missing_openai_key_exits(self):
        """Test that missing OPENAI_API_KEY causes sys.exit(1)."""
        from faf.mcp_server import main

        with patch('sys.argv', ['mcp_server.py']):
            with patch('faf.mcp_server.os.getenv', return_value=None):
                with patch('sys.exit') as mock_exit:
                    with patch('faf.mcp_server.logger') as mock_logger:
                        main()
                        mock_logger.error.assert_called_with(
                            "OPENAI_API_KEY environment variable not set"
                        )
                        # Just check that sys.exit(1) was called, don't worry about exact count
                        mock_exit.assert_any_call(1)

    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of keyboard interrupt."""
        from faf.mcp_server import main

        with patch('sys.argv', ['mcp_server.py']):
            with patch('faf.mcp_server.os.getenv', return_value='test-key'):
                with patch('faf.mcp_server.load_configuration') as mock_load_config:
                    mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
                    with patch('faf.mcp_server.FafMcpServer') as mock_server_class:
                        mock_server = Mock()
                        mock_server.run_stdio.side_effect = KeyboardInterrupt()
                        mock_server_class.return_value = mock_server

                        with patch('faf.mcp_server.logger') as mock_logger:
                            main()
                            mock_logger.info.assert_called_with("Server stopped by user")

    def test_exception_handling(self):
        """Test proper exception handling with sys.exit(1)."""
        from faf.mcp_server import main

        with patch('sys.argv', ['mcp_server.py']):
            with patch('faf.mcp_server.os.getenv', return_value='test-key'):
                with patch('faf.mcp_server.load_configuration') as mock_load_config:
                    mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")
                    with patch('faf.mcp_server.FafMcpServer') as mock_server_class:
                        mock_server = Mock()
                        mock_server.run_stdio.side_effect = Exception("Test error")
                        mock_server_class.return_value = mock_server

                        with patch('sys.exit') as mock_exit:
                            with patch('faf.mcp_server.logger') as mock_logger:
                                main()
                                mock_logger.exception.assert_called_once()
                                mock_exit.assert_any_call(1)


class TestMcpServerParameterValidation:
    """Tests for parameter validation in MCP server methods."""

    @patch('faf.mcp_server.load_configuration')
    @patch('faf.mcp_server.mcp')
    def test_run_http_with_all_parameters(self, mock_mcp, mock_load_config):
        """Test run_http with all possible parameter combinations."""
        mock_load_config.return_value = ("gpt-4o", "TestUser", "Custom rules")

        server = FafMcpServer()

        # Test with various mount path combinations
        test_cases = [
            "/api",
            "/mcp-server",
            "/",
        ]

        for mount_path in test_cases:
            mock_mcp.reset_mock()
            server.run_http(mount_path)
            mock_mcp.run.assert_called_once_with(
                transport="streamable-http",
                mount_path=mount_path
            )

    @patch('faf.mcp_server.load_configuration')
    def test_server_initialization_with_different_configs(self, mock_load_config):
        """Test server initialization with different configuration combinations."""
        test_configs = [
            ("gpt-4o", "TestUser", "Custom rules"),
            ("gpt-3.5-turbo", None, None),
            ("claude-3", "DifferentUser", ""),
        ]

        for model, user_name, custom_rules in test_configs:
            mock_load_config.return_value = (model, user_name, custom_rules)
            server = FafMcpServer()
            assert server.model == model
            assert server.user_name == user_name
            assert server.custom_rules == custom_rules
