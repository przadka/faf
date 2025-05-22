import json
import pytest
from unittest.mock import patch, Mock


class TestMcpTools:
    """Test cases for MCP tool wrappers."""

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.follow_up_then_sync')
    async def test_follow_up_then(self, mock_sync_func):
        """Test that MCP follow_up_then tool wrapper calls sync function and returns dict."""
        from faf.mcp_tools import follow_up_then
        
        mock_sync_func.return_value = json.dumps({
            "command": "follow_up_then",
            "payload": {"date": "tomorrow", "message": "Call John"},
            "prompt": "Remind me to call John tomorrow."
        })
        
        result = await follow_up_then(
            "Remind me to call John tomorrow.", 
            "tomorrow", 
            "Call John"
        )
        
        mock_sync_func.assert_called_once_with(
            "Remind me to call John tomorrow.", 
            "tomorrow", 
            "Call John"
        )
        assert isinstance(result, dict)
        assert result["command"] == "follow_up_then"
        assert result["payload"]["date"] == "tomorrow"
        assert result["payload"]["message"] == "Call John"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.note_to_self_sync')
    async def test_note_to_self(self, mock_sync_func):
        """Test that MCP note_to_self tool wrapper calls sync function and returns dict."""
        from faf.mcp_tools import note_to_self
        
        mock_sync_func.return_value = json.dumps({
            "command": "note_to_self",
            "payload": {"message": "Buy milk"},
            "prompt": "Buy milk."
        })
        
        result = await note_to_self("Buy milk.", "Buy milk")
        
        mock_sync_func.assert_called_once_with("Buy milk.", "Buy milk")
        assert isinstance(result, dict)
        assert result["command"] == "note_to_self"
        assert result["payload"]["message"] == "Buy milk"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.save_url_sync')
    async def test_save_url_valid(self, mock_sync_func):
        """Test that MCP save_url tool wrapper handles valid URLs correctly."""
        from faf.mcp_tools import save_url
        
        mock_sync_func.return_value = json.dumps({
            "command": "save_url",
            "payload": {"url": "https://example.com"},
            "prompt": "https://example.com"
        })
        
        result = await save_url("https://example.com", "https://example.com")
        
        mock_sync_func.assert_called_once_with("https://example.com", "https://example.com")
        assert isinstance(result, dict)
        assert result["command"] == "save_url"
        assert result["payload"]["url"] == "https://example.com"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.save_url_sync')
    async def test_save_url_invalid(self, mock_sync_func):
        """Test that MCP save_url tool wrapper raises ValueError for invalid URLs."""
        from faf.mcp_tools import save_url
        
        mock_sync_func.return_value = "Error: Invalid URL"
        
        with pytest.raises(ValueError, match="Error: Invalid URL"):
            await save_url("not a url", "not a url")

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.journaling_topic_sync')
    async def test_journaling_topic(self, mock_sync_func):
        """Test that MCP journaling_topic tool wrapper calls sync function and returns dict."""
        from faf.mcp_tools import journaling_topic
        
        mock_sync_func.return_value = json.dumps({
            "command": "journaling_topic",
            "payload": {"topic": "Trip to the mountains"},
            "prompt": "I want to journal about my trip."
        })
        
        result = await journaling_topic(
            "I want to journal about my trip.", 
            "Trip to the mountains"
        )
        
        mock_sync_func.assert_called_once_with(
            "I want to journal about my trip.", 
            "Trip to the mountains"
        )
        assert isinstance(result, dict)
        assert result["command"] == "journaling_topic"
        assert result["payload"]["topic"] == "Trip to the mountains"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.va_request_sync')
    async def test_va_request(self, mock_sync_func):
        """Test that MCP va_request tool wrapper calls sync function and returns dict."""
        from faf.mcp_tools import va_request
        
        mock_sync_func.return_value = json.dumps({
            "command": "va_request",
            "payload": {"title": "Dinner reservation", "request": "Book a table for two at 7pm."},
            "prompt": "VA: Book a table for two."
        })
        
        result = await va_request(
            "VA: Book a table for two.", 
            "Dinner reservation", 
            "Book a table for two at 7pm."
        )
        
        mock_sync_func.assert_called_once_with(
            "VA: Book a table for two.", 
            "Dinner reservation", 
            "Book a table for two at 7pm."
        )
        assert isinstance(result, dict)
        assert result["command"] == "va_request"
        assert result["payload"]["title"] == "Dinner reservation"
        assert result["payload"]["request"] == "Book a table for two at 7pm."

    def test_tool_docstrings_exist(self):
        """Test that all MCP tools have proper docstrings for MCP documentation."""
        import faf.mcp_tools as mcp_tools
        
        tools = [
            mcp_tools.follow_up_then,
            mcp_tools.note_to_self,
            mcp_tools.save_url,
            mcp_tools.journaling_topic,
            mcp_tools.va_request
        ]
        
        for tool in tools:
            assert tool.__doc__ is not None, f"Tool {tool.__name__} missing docstring"
            assert len(tool.__doc__.strip()) > 0, f"Tool {tool.__name__} has empty docstring"
            # Check that docstring contains key information
            assert "Args:" in tool.__doc__, f"Tool {tool.__name__} docstring missing Args section"
            assert "Returns:" in tool.__doc__, f"Tool {tool.__name__} docstring missing Returns section"

    def test_mcp_imports_work(self):
        """Test that MCP tools can be imported without errors."""
        try:
            import faf.mcp_tools
            import faf.mcp_server
            # If we get here, imports worked
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import MCP modules: {e}")

    @pytest.mark.asyncio
    async def test_all_tools_are_async(self):
        """Test that all MCP tools are properly async functions."""
        import faf.mcp_tools as mcp_tools
        import inspect
        
        tools = [
            mcp_tools.follow_up_then,
            mcp_tools.note_to_self,
            mcp_tools.save_url,
            mcp_tools.journaling_topic,
            mcp_tools.va_request
        ]
        
        for tool in tools:
            assert inspect.iscoroutinefunction(tool), f"Tool {tool.__name__} is not an async function"