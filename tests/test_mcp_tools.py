import json
import pytest
from unittest.mock import patch


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

        # Test that validation catches invalid URL before sync function is called
        with pytest.raises(ValueError, match="URL must start with"):
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
            assert "Returns:" in tool.__doc__, (
                f"Tool {tool.__name__} docstring missing Returns section"
            )

    def test_mcp_imports_work(self):
        """Test that MCP tools can be imported without errors."""
        try:
            __import__('faf.mcp_tools')
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
            assert inspect.iscoroutinefunction(tool), (
                f"Tool {tool.__name__} is not an async function"
            )


class TestMcpToolsValidation:
    """Test cases for MCP tools input validation."""

    @pytest.mark.asyncio
    async def test_follow_up_then_validation(self):
        """Test follow_up_then input validation."""
        from faf.mcp_tools import follow_up_then

        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await follow_up_then("", "tomorrow", "Call John")

        # Test empty date
        with pytest.raises(ValueError, match="Date cannot be empty"):
            await follow_up_then("Call John tomorrow", "", "Call John")

        # Test empty message
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await follow_up_then("Call John tomorrow", "tomorrow", "")

        # Test invalid date with spaces
        with pytest.raises(ValueError, match="Date cannot contain ' ' characters"):
            await follow_up_then("Call John tomorrow", "tomorrow 3pm", "Call John")

        # Test invalid date with "this"
        with pytest.raises(ValueError, match="Date cannot start with 'this'"):
            await follow_up_then("Call John this Monday", "thisMonday", "Call John")

        # Test invalid date with colons
        with pytest.raises(ValueError, match="Time should not contain colons"):
            await follow_up_then("Call John at 3:00pm", "tomorrow3:00pm", "Call John")

    @pytest.mark.asyncio
    async def test_note_to_self_validation(self):
        """Test note_to_self input validation."""
        from faf.mcp_tools import note_to_self

        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await note_to_self("", "Buy milk")

        # Test empty message
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await note_to_self("Buy milk", "")

        # Test invalid priority
        with pytest.raises(ValueError, match="Priority must be one of: low, normal, high"):
            await note_to_self("Buy milk", "Buy milk", "urgent")

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.note_to_self_sync')
    async def test_note_to_self_with_priority(self, mock_sync_func):
        """Test note_to_self with priority parameter."""
        from faf.mcp_tools import note_to_self

        mock_sync_func.return_value = json.dumps({
            "command": "note_to_self",
            "payload": {"message": "Buy milk"},
            "prompt": "Buy milk."
        })

        result = await note_to_self("Buy milk.", "Buy milk", "high")

        assert result["payload"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_save_url_validation(self):
        """Test save_url input validation."""
        from faf.mcp_tools import save_url

        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await save_url("", "https://example.com")

        # Test empty URL
        with pytest.raises(ValueError, match="URL cannot be empty"):
            await save_url("Check this out", "")

        # Test invalid URL without protocol
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            await save_url("Check this out", "example.com")

        # Test URL with spaces
        with pytest.raises(ValueError, match="URL cannot contain spaces"):
            await save_url("Check this out", "https://example .com")

        # Test URL without domain
        with pytest.raises(ValueError, match="URL must contain a domain with a dot"):
            await save_url("Check this out", "https://localhost")

    @pytest.mark.asyncio
    async def test_journaling_topic_validation(self):
        """Test journaling_topic input validation."""
        from faf.mcp_tools import journaling_topic

        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await journaling_topic("", "My day today")

        # Test empty topic
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            await journaling_topic("Journal about my day", "")

        # Test empty category
        with pytest.raises(ValueError, match="Category cannot be empty"):
            await journaling_topic("Journal about my day", "My day today", "")

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.journaling_topic_sync')
    async def test_journaling_topic_with_category(self, mock_sync_func):
        """Test journaling_topic with category parameter."""
        from faf.mcp_tools import journaling_topic

        mock_sync_func.return_value = json.dumps({
            "command": "journaling_topic",
            "payload": {"topic": "My day today"},
            "prompt": "Journal about my day."
        })

        result = await journaling_topic("Journal about my day.", "My day today", "personal")

        assert result["payload"]["category"] == "personal"

    @pytest.mark.asyncio
    async def test_va_request_validation(self):
        """Test va_request input validation."""
        from faf.mcp_tools import va_request

        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await va_request("", "Book restaurant", "Book a table")

        # Test empty title
        with pytest.raises(ValueError, match="Title cannot be empty"):
            await va_request("VA: Book a restaurant", "", "Book a table")

        # Test empty request
        with pytest.raises(ValueError, match="Request cannot be empty"):
            await va_request("VA: Book a restaurant", "Book restaurant", "")

        # Test missing VA keywords
        with pytest.raises(ValueError, match="VA requests must include"):
            await va_request("Book a restaurant", "Book restaurant", "Book a table")

        # Test invalid urgency
        with pytest.raises(ValueError, match="Urgency must be one of"):
            await va_request("VA: Book a restaurant", "Book restaurant", "Book a table", "critical")

        # Test title too long
        long_title = "A" * 101
        with pytest.raises(ValueError, match="Title should be short"):
            await va_request("VA: Book a restaurant", long_title, "Book a table")

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.va_request_sync')
    async def test_va_request_with_urgency(self, mock_sync_func):
        """Test va_request with urgency parameter."""
        from faf.mcp_tools import va_request

        mock_sync_func.return_value = json.dumps({
            "command": "va_request",
            "payload": {"title": "Book restaurant", "request": "Book a table"},
            "prompt": "VA: Book a restaurant."
        })

        result = await va_request(
            "VA: Book a restaurant.", "Book restaurant", "Book a table", "urgent"
        )

        assert result["payload"]["urgency"] == "urgent"

    def test_validation_functions(self):
        """Test individual validation functions."""
        from faf.validation import (
            validate_non_empty_string, validate_url, validate_date_format,
            validate_priority, validate_va_keywords
        )

        # Test validate_non_empty_string
        with pytest.raises(ValueError, match="Test cannot be empty"):
            validate_non_empty_string("", "Test")

        with pytest.raises(ValueError, match="Test cannot be empty"):
            validate_non_empty_string("   ", "Test")

        # Test validate_url
        with pytest.raises(ValueError, match="URL must start with"):
            validate_url("example.com")

        # Test validate_date_format
        with pytest.raises(ValueError, match="Date cannot contain"):
            validate_date_format("tomorrow 3pm")

        # Test validate_priority
        with pytest.raises(ValueError, match="Priority must be one of"):
            validate_priority("critical")

        # Test validate_va_keywords
        with pytest.raises(ValueError, match="VA requests must include"):
            validate_va_keywords("Book a restaurant")


class TestMcpToolsFileSaving:
    """Test cases for file saving functionality in MCP tools."""

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.note_to_self_sync')
    async def test_note_to_self_saves_file(self, mock_sync_func, mock_write_file):
        """Test that note_to_self saves JSON file to disk."""
        from faf.mcp_tools import note_to_self

        # Mock the sync function return
        test_json = json.dumps({
            "command": "note_to_self",
            "payload": {"message": "Test message"},
            "prompt": "Test prompt"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.return_value = "Success: Data written to test.json"

        # Call the function
        result = await note_to_self("Test prompt", "Test message")

        # Verify sync function was called
        mock_sync_func.assert_called_once_with("Test prompt", "Test message")

        # Verify write_to_file was called with the JSON
        mock_write_file.assert_called_once()
        call_args = mock_write_file.call_args[0][0]
        saved_data = json.loads(call_args)
        assert saved_data["command"] == "note_to_self"
        assert saved_data["payload"]["message"] == "Test message"

        # Verify return value
        assert result["command"] == "note_to_self"
        assert result["payload"]["message"] == "Test message"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.follow_up_then_sync')
    async def test_follow_up_then_saves_file(self, mock_sync_func, mock_write_file):
        """Test that follow_up_then saves JSON file to disk."""
        from faf.mcp_tools import follow_up_then

        test_json = json.dumps({
            "command": "follow_up_then",
            "payload": {"date": "tomorrow", "message": "Call John"},
            "prompt": "Remind me tomorrow"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.return_value = "Success: Data written to test.json"

        result = await follow_up_then("Remind me tomorrow", "tomorrow", "Call John")

        mock_sync_func.assert_called_once_with("Remind me tomorrow", "tomorrow", "Call John")
        mock_write_file.assert_called_once_with(test_json)
        assert result["command"] == "follow_up_then"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.save_url_sync')
    async def test_save_url_saves_file(self, mock_sync_func, mock_write_file):
        """Test that save_url saves JSON file to disk."""
        from faf.mcp_tools import save_url

        test_json = json.dumps({
            "command": "save_url",
            "payload": {"url": "https://example.com"},
            "prompt": "Save this URL"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.return_value = "Success: Data written to test.json"

        result = await save_url("Save this URL", "https://example.com")

        mock_sync_func.assert_called_once_with("Save this URL", "https://example.com")
        mock_write_file.assert_called_once_with(test_json)
        assert result["command"] == "save_url"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.va_request_sync')
    async def test_va_request_saves_file_with_urgency(self, mock_sync_func, mock_write_file):
        """Test that va_request saves JSON file with urgency parameter."""
        from faf.mcp_tools import va_request

        test_json = json.dumps({
            "command": "va_request",
            "payload": {"title": "Book restaurant", "request": "Book a table"},
            "prompt": "VA: Book restaurant"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.return_value = "Success: Data written to test.json"

        await va_request(
            "VA: Book restaurant", "Book restaurant", "Book a table", "urgent"
        )

        mock_sync_func.assert_called_once_with(
            "VA: Book restaurant", "Book restaurant", "Book a table"
        )

        # Verify write_to_file was called with urgency added
        mock_write_file.assert_called_once()
        call_args = mock_write_file.call_args[0][0]
        saved_data = json.loads(call_args)
        assert saved_data["payload"]["urgency"] == "urgent"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.journaling_topic_sync')
    async def test_journaling_topic_saves_file_with_category(self, mock_sync_func, mock_write_file):
        """Test that journaling_topic saves JSON file with category parameter."""
        from faf.mcp_tools import journaling_topic

        test_json = json.dumps({
            "command": "journaling_topic",
            "payload": {"topic": "My day"},
            "prompt": "Journal about my day"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.return_value = "Success: Data written to test.json"

        await journaling_topic("Journal about my day", "My day", "personal")

        mock_sync_func.assert_called_once_with("Journal about my day", "My day")

        # Verify write_to_file was called with category added
        mock_write_file.assert_called_once()
        call_args = mock_write_file.call_args[0][0]
        saved_data = json.loads(call_args)
        assert saved_data["payload"]["category"] == "personal"

    @pytest.mark.asyncio
    @patch('faf.mcp_tools.write_to_file')
    @patch('faf.mcp_tools.note_to_self_sync')
    async def test_file_saving_error_handling(self, mock_sync_func, mock_write_file):
        """Test that file saving errors are handled gracefully."""
        from faf.mcp_tools import note_to_self

        test_json = json.dumps({
            "command": "note_to_self",
            "payload": {"message": "Test message"},
            "prompt": "Test prompt"
        })
        mock_sync_func.return_value = test_json
        mock_write_file.side_effect = IOError("Unable to write file")

        # Should not raise exception even if file saving fails
        result = await note_to_self("Test prompt", "Test message")

        # Function should still return the result
        assert result["command"] == "note_to_self"
        assert result["payload"]["message"] == "Test message"
