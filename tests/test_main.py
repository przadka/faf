import os
import json
import tempfile
import pytest
from unittest import mock
from src.faf import main, tools

def test_get_tool_function_info():
    """Test that get_tool_function_info extracts correct metadata from a tool function."""
    info = main.get_tool_function_info(tools.note_to_self)
    assert info["function"]["name"] == "note_to_self"
    assert "description" in info["function"]
    assert "parameters" in info["function"]

def test_collect_functions_info():
    """Test that collect_functions_info returns a list of function metadata for given tool functions."""
    infos = main.collect_functions_info(tools.note_to_self, tools.save_url)
    assert isinstance(infos, list)
    assert infos[0]["function"]["name"] == "note_to_self"
    assert infos[1]["function"]["name"] == "save_url"

def test_tools_list():
    """Test that tools_list returns all expected tool function names."""
    tool_list = main.tools_list()
    names = [item["function"]["name"] for item in tool_list]
    assert set(["note_to_self", "save_url", "follow_up_then", "va_request", "journaling_topic"]).issubset(set(names))

def test_call_tool_function_valid():
    """Test that call_tool_function correctly calls a valid tool and returns expected output."""
    action = {"name": "note_to_self", "arguments": {"prompt": "Test", "message": "Test message"}}
    result = main.call_tool_function(action)
    assert result["tool_call_name"] == "note_to_self"
    data = json.loads(result["output"])
    assert data["command"] == "note_to_self"

def test_call_tool_function_invalid():
    """Test that call_tool_function raises ValueError for an unknown tool name."""
    action = {"name": "not_a_tool", "arguments": {}}
    with pytest.raises(ValueError):
        main.call_tool_function(action)

def test_write_to_file_success(monkeypatch):
    """Test that write_to_file writes a valid JSON string to a file and returns a success message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("FAF_JSON_OUTPUT_PATH", tmpdir)
        data = json.dumps({"command": "test", "payload": {"foo": "bar"}})
        msg = main.write_to_file(data)
        assert "Success: Data written to" in msg
        files = os.listdir(tmpdir)
        assert any(f.endswith("_test.json") for f in files)

def test_write_to_file_invalid_json():
    """Test that write_to_file raises ValueError when given invalid JSON input."""
    with pytest.raises(ValueError):
        main.write_to_file("not a json string")

def test_load_configuration(monkeypatch):
    """Test that load_configuration loads model, user name, and custom rules from environment and file."""
    monkeypatch.setenv("FAF_MODEL", "test-model")
    monkeypatch.setenv("FAF_USER_NAME", "TestUser")
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("- Custom rule\n")
        rules_path = f.name
    monkeypatch.setenv("FAF_CUSTOM_RULES_FILE", rules_path)
    model, user, rules = main.load_configuration()
    assert model == "test-model"
    assert user == "TestUser"
    assert "Custom rule" in rules
    os.remove(rules_path)

def test_improve_user_input_mocked():
    """Test improve_user_input returns the expected improved text using a mocked LLM response."""
    with mock.patch("src.faf.main.completion") as mock_completion:
        class MockMessage:
            content = "Buy milk. #note_to_self"
        mock_completion.return_value = mock.Mock(choices=[mock.Mock(message=MockMessage())])
        result = main.improve_user_input("Buy milk.", "John", "", "fake-model")
        assert result == "Buy milk. #note_to_self"

def test_convert_to_json_mocked():
    """Test convert_to_json returns the expected JSON output using a mocked LLM response and tool call."""
    with mock.patch("src.faf.main.completion") as mock_completion, \
         mock.patch("src.faf.main.call_tool_function") as mock_call_tool_function:
        # Mock the LLM response
        class MockToolCall:
            function = mock.Mock(name="note_to_self", arguments={"prompt": "Buy milk.", "message": "Buy milk."})
        class MockMessage:
            content = ""
            tool_calls = [MockToolCall()]
        mock_completion.return_value = mock.Mock(
            choices=[mock.Mock(message=MockMessage())],
            created=123,
            model="fake-model",
            usage=mock.Mock(prompt_tokens=1, completion_tokens=1, total_tokens=2)
        )
        # Mock the tool function output
        mock_call_tool_function.return_value = {"tool_call_name": "note_to_self", "output": json.dumps({"command": "note_to_self", "payload": {"message": "Buy milk."}, "prompt": "Buy milk."})}
        tools_list_val = main.tools_list()
        result = main.convert_to_json("Buy milk.", "John", "", "fake-model", tools_list_val)
        assert result["command"] == "note_to_self"
        assert result["payload"]["message"] == "Buy milk."
        assert result["prompt"] == "Buy milk."
        assert result["model"] == "fake-model"
        assert result["created"] == 123 