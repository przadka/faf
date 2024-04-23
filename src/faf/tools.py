import json
import os
import re
from datetime import datetime


def write_to_file(prompt:str, command: str, payload: dict) -> str:
    data = {
        "prompt": prompt,
        "command": command,
        "payload": payload
    }

    # get the output directory from environment variable
    directory = os.getenv('FAF_JSON_OUTPUT_PATH')

    # if directory is not set, use project root directory
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))

    # create directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # use current timestamp to generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{command}.json"

    # write the data to the file
    with open(os.path.join(directory, filename), 'w') as outfile:
        json.dump(data, outfile)
        
    return f"Success: Data written to {filename} in directory {directory}."


def follow_up_then(prompt:str, date: str, message: str) -> str:
    """
    Send a follow-up reminder with the given date and message.
    Use only if there is a specific date provided or
    some time reference like "tomorrow" or "in 2 days".
    Additional contraits for the date:
      - Do not use "this" in the date like "thisMonday" or "thisTuesday" as FUT does not support them.
      - Do not user "in a week", "in two weeks" or "in a month" replace them with "1week", 
      "2weeks" and "1month" respectively. 
      - Date cannot have any spaces, dots or commas. 

    Args:
        prompt: Full prompt provided by the user.
        date: Date of the follow-up in the format like "1August", "tomorrow3pm" or "in2days".
        message: Message to send.

    Returns:
        Status message.
    """

    # the following shouln't be needed as the LLM already does knows the date specs
    # and should generate the date in the correct format
    # but just in case, we do it here as well

    date = date.replace("this", "")
    date = date.replace(" ", "")
    date = date.replace(".", "")
    date = date.replace(",", "")

    return write_to_file(prompt, "follow_up_then", {"date": date, "message": message})


def user_note(prompt:str, message: str) -> str:
    """
    Send a note to user with the given message.
    Useful for simple todos, reminders and short-term follow ups.

    Args:
        prompt: Full prompt provided by the user.
        message: Message to send. Should be based on the prompt, without any additional information.

    Returns:
        Status message.
    """

    return write_to_file(prompt, "note_to_self", {"message": message})


def save_url(prompt:str, url: str) -> str:
    """
    Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.

    Args:
        prompt: Full prompt provided by the user.
        user_url: URL to append to the URL list.

    Returns:
        The response from the webhook concatenated with the input message.
    """

    # check if the input is URL-like, starts with http or https, has a dot in the middle,
    # and does not have any spaces

    if not (url.startswith("http") or  "." in url) or  " " in url:
        return "Error: The input is not a valid URL." 
    
    return write_to_file(prompt, "save_url", {"url": url})

def va_request(prompt:str, title:str, request: str) -> str:
    """
    Send a request to the VA with the given message. Use only if the input explicitly asks for a virtual assistant or VA.
    Use ONLY if the prompt includes the word "virtual assistant" or "VA".

    Args:
        prompt: Full prompt provided by the user.
        title: Title of the request, used as a Trello card title. Keep it short.
        request: Request to send.

    Returns:
        Status message.
    """

    # check if the prompt includes the word "virtual assistant" or "VA", as a separate word
    if "virtual assistant" not in prompt.lower() and not re.search(r'\bva\b', prompt.lower()):
        return "Error: The input does not explicitly ask for a virtual assistant or VA."
        
    return write_to_file(prompt, "va_request", {"title": title, "request": request})

