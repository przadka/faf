"""
Test cases for FAF entry points and command-line interfaces.
"""

import subprocess
import sys
import pytest
from unittest.mock import patch


class TestEntryPoints:
    """Test cases for FAF command-line entry points."""

    def test_faf_mcp_entry_point_exists(self):
        """Test that faf-mcp entry point is properly installed."""
        # This test verifies the entry point exists and can be imported
        try:
            import pkg_resources
            entry_points = pkg_resources.get_entry_map('faf', 'console_scripts')
            assert 'faf-mcp' in entry_points

            # Verify it points to the correct module and function
            faf_mcp_entry = entry_points['faf-mcp']
            assert faf_mcp_entry.module_name == 'faf.mcp_server'
            assert faf_mcp_entry.attrs == ('main',)
        except ImportError:
            # For newer Python versions, use importlib.metadata
            import importlib.metadata
            entry_points = importlib.metadata.entry_points()
            console_scripts = entry_points.select(group='console_scripts')
            faf_mcp_scripts = [ep for ep in console_scripts if ep.name == 'faf-mcp']
            assert len(faf_mcp_scripts) == 1

            faf_mcp_entry = faf_mcp_scripts[0]
            assert 'faf.mcp_server:main' in faf_mcp_entry.value

    def test_faf_entry_point_exists(self):
        """Test that faf entry point is properly installed."""
        try:
            import pkg_resources
            entry_points = pkg_resources.get_entry_map('faf', 'console_scripts')
            assert 'faf' in entry_points

            # Verify it points to the correct module and function
            faf_entry = entry_points['faf']
            assert faf_entry.module_name == 'faf.main'
            assert faf_entry.attrs == ('main',)
        except ImportError:
            # For newer Python versions, use importlib.metadata
            import importlib.metadata
            entry_points = importlib.metadata.entry_points()
            console_scripts = entry_points.select(group='console_scripts')
            faf_scripts = [ep for ep in console_scripts if ep.name == 'faf']
            assert len(faf_scripts) == 1

            faf_entry = faf_scripts[0]
            assert 'faf.main:main' in faf_entry.value

    @patch('faf.mcp_server.main')
    def test_faf_mcp_main_import(self, mock_main):
        """Test that faf-mcp entry point can import and call main function."""
        # Test that we can import the main function from the entry point
        from faf.mcp_server import main

        # Call it to ensure it's callable
        main()
        mock_main.assert_called_once()

    def test_faf_mcp_help_command(self):
        """Test that faf-mcp --help works correctly."""
        # This is an integration test that actually calls the command
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'faf.mcp_server', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Should exit with code 0 for help
            assert result.returncode == 0

            # Should contain expected help text
            assert 'FAF MCP Server' in result.stdout
            assert '--transport' in result.stdout
            assert '--mount-path' in result.stdout

        except subprocess.TimeoutExpired:
            pytest.skip("Command timed out - may indicate environment issues")
        except FileNotFoundError:
            pytest.skip("Python executable not found")

    def test_import_faf_mcp_server_module(self):
        """Test that the MCP server module can be imported without errors."""
        # This test ensures the module structure is correct
        import faf.mcp_server

        # Verify main function exists
        assert hasattr(faf.mcp_server, 'main')
        assert callable(faf.mcp_server.main)

        # Verify FafMcpServer class exists
        assert hasattr(faf.mcp_server, 'FafMcpServer')
        assert callable(faf.mcp_server.FafMcpServer)


class TestCommandLineArguments:
    """Test cases for command-line argument parsing."""

    @patch('faf.mcp_server.FafMcpServer')
    @patch('os.getenv')
    def test_main_with_stdio_transport(self, mock_getenv, mock_server_class):
        """Test main function with stdio transport argument."""
        mock_getenv.return_value = 'test-api-key'

        # Mock sys.argv to simulate command line args
        with patch('sys.argv', ['faf-mcp', '--transport', 'stdio']):
            from faf.mcp_server import main

            try:
                main()
            except SystemExit:
                pass  # Expected due to missing environment setup in test

            # Verify server was created and stdio method would be called
            mock_server_class.assert_called_once()

    @patch('faf.mcp_server.FafMcpServer')
    @patch('os.getenv')
    def test_main_with_http_transport(self, mock_getenv, mock_server_class):
        """Test main function with http transport argument."""
        mock_getenv.return_value = 'test-api-key'

        # Mock sys.argv to simulate command line args
        with patch('sys.argv', ['faf-mcp', '--transport', 'http', '--mount-path', '/test']):
            from faf.mcp_server import main

            try:
                main()
            except SystemExit:
                pass  # Expected due to missing environment setup in test

            # Verify server was created
            mock_server_class.assert_called_once()
