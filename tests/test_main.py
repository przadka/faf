import os
import json
import tempfile
import pytest
from unittest import mock
from src.faf import main, tools

def test_get_tool_function_info():
    info = main.get_tool_function_info(tools.note_to_self)
    assert info["function"]["name"] == "note_to_self"
    assert "description" in info["function"]
    assert "parameters" in info["function"]

def test_collect_functions_info():
    infos = main.collect_functions_info(tools.note_to_self, tools.save_url)
    assert isinstance(infos, list)
    assert infos[0]["function"]["name"] == "note_to_self"
    assert infos[1]["function"]["name"] == "save_url"

def test_tools_list():
    tool_list = main.tools_list()
    names = [item["function"]["name"] for item in tool_list]
    assert set(["note_to_self", "save_url", "follow_up_then", "va_request", "journaling_topic"]).issubset(set(names))

def test_call_tool_function_valid():
    action = {"name": "note_to_self", "arguments": {"prompt": "Test", "message": "Test message"}}
    result = main.call_tool_function(action)
    assert result["tool_call_name"] == "note_to_self"
    data = json.loads(result["output"])
    assert data["command"] == "note_to_self"

def test_call_tool_function_invalid():
    action = {"name": "not_a_tool", "arguments": {}}
    with pytest.raises(ValueError):
        main.call_tool_function(action)

def test_write_to_file_success(monkeypatch):
    # Use a temp directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("FAF_JSON_OUTPUT_PATH", tmpdir)
        data = json.dumps({"command": "test", "payload": {"foo": "bar"}})
        msg = main.write_to_file(data)
        assert "Success: Data written to" in msg
        # Check that a file was created
        files = os.listdir(tmpdir)
        assert any(f.endswith("_test.json") for f in files)

def test_write_to_file_invalid_json():
    with pytest.raises(ValueError):
        main.write_to_file("not a json string")

def test_load_configuration(monkeypatch):
    monkeypatch.setenv("FAF_MODEL", "test-model")
    monkeypatch.setenv("FAF_USER_NAME", "TestUser")
    # Create a temp rules file
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("- Custom rule\n")
        rules_path = f.name
    monkeypatch.setenv("FAF_CUSTOM_RULES_FILE", rules_path)
    model, user, rules = main.load_configuration()
    assert model == "test-model"
    assert user == "TestUser"
    assert "Custom rule" in rules
    os.remove(rules_path) 