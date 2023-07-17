import os

import requests
from langchain.tools import StructuredTool
from helpers import get_env_var

def post_to_webhook(url: str, command: str, payload: dict) -> str:
    data = {
        "command": command,
        "payload": payload
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        status_message = f"Success: assistant webhook called successfully for {command}."
    elif response.status_code == 400:
        status_message = "Failure: Bad request, please check the sent data."
    elif response.status_code == 401:
        status_message = "Failure: Unauthorized, please check your authentication."
    elif response.status_code == 404:
        status_message = "Failure: URL not found, please check the webhook URL."
    else:
        status_message = f"Failure: Unexpected status code {response.status_code}."
        
    return f"{status_message}({payload['message']})"

def follow_up_then(date: str, message: str) -> str:
    """
    Send a follow-up reminder with the given date and message.

    Args:
        date: Date of the follow-up in the format like "1August", "tomorrow3pm" or "in2days".
        message: Message to send.

    Returns:
        The response from the webhook concatenated with the input message.
    """
    key = get_env_var('IFTTT_KEY')
    url = f"https://maker.ifttt.com/trigger/assistant_requested/json/with/key/{key}"

    return post_to_webhook(url, "follow_up_then", {"date": date, "message": message})

def self_note(message: str) -> str:
    """
    Send a note to self email with the given message.
    Useful for simple todos, reminders and short-term follow ups.

    Args:
        message: Message to send.

    Returns:
        The response from the webhook concatenated with the input message.
    """
    key = get_env_var('IFTTT_KEY')
    url = f"https://maker.ifttt.com/trigger/assistant_requested/json/with/key/{key}"

    return post_to_webhook(url, "note_to_self", {"message": message})

fut = StructuredTool.from_function(follow_up_then, name="Follow Up Then")
note = StructuredTool.from_function(self_note, name="Note to Self")

tools = [note, fut]
