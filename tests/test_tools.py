import json
import pytest
from src.faf import tools

def test_follow_up_then():
    prompt = "Remind me to call John tomorrow."
    date = "tomorrow"
    message = "Call John"
    result = tools.follow_up_then(prompt, date, message)
    data = json.loads(result)
    assert data["command"] == "follow_up_then"
    assert data["payload"]["date"] == "tomorrow"
    assert data["payload"]["message"] == message
    assert data["prompt"] == prompt

def test_note_to_self():
    prompt = "Buy milk."
    message = "Buy milk."
    result = tools.note_to_self(prompt, message)
    data = json.loads(result)
    assert data["command"] == "note_to_self"
    assert data["payload"]["message"] == message
    assert data["prompt"] == prompt

def test_save_url_valid():
    prompt = "https://example.com"
    url = "https://example.com"
    result = tools.save_url(prompt, url)
    data = json.loads(result)
    assert data["command"] == "save_url"
    assert data["payload"]["url"] == url
    assert data["prompt"] == prompt

def test_save_url_invalid():
    prompt = "not a url"
    url = "not a url"
    result = tools.save_url(prompt, url)
    assert result.startswith("Error")

def test_journaling_topic():
    prompt = "I want to journal about my trip."
    topic = "Trip to the mountains"
    result = tools.journaling_topic(prompt, topic)
    data = json.loads(result)
    assert data["command"] == "journaling_topic"
    assert data["payload"]["topic"] == topic
    assert data["prompt"] == prompt

def test_va_request():
    prompt = "VA: Book a table for two."
    title = "Dinner reservation"
    request = "Book a table for two at 7pm."
    result = tools.va_request(prompt, title, request)
    data = json.loads(result)
    assert data["command"] == "va_request"
    assert data["payload"]["title"] == title
    assert data["payload"]["request"] == request
    assert data["prompt"] == prompt 